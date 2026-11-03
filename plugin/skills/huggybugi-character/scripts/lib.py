"""허기부기 48px 캐릭터·아이템을 코드로 그리는 도구.

그림 한 장 = 48줄 x 48글자 격자(list[str]). '.' 은 투명, 나머지 글자는 COLORS 의 색.
render(fill) 이 칸마다 fill(x, y) 를 불러 격자를 만들고, 빈 칸과 맞닿은 칸을 외곽선 'K' 로 바꾼다.
"""

from __future__ import annotations

import io
import math
import struct
import sys
import zipfile
from pathlib import Path
from typing import Callable

try:
    from PIL import Image
except ImportError:
    sys.exit('Pillow 가 없어요. 먼저 설치하세요: python3 -m pip install pillow')

FRAME = 48
# 얼굴(눈·입·볼)을 오른쪽으로 옮기는 칸 수. 살짝 오른쪽을 보는 모습(왼쪽으로 갈 땐 앱이 뒤집는다).
TURN = 3

Grid = list[str]

CHARACTER_ANIMS = ['idle', 'walk', 'sleep', 'poked', 'throw', 'hit', 'jump', 'eat', 'wave', 'happy', 'offline']
ITEM_ANIMS = ['fly', 'impact']
# 앱 만들기 창 권장 fps(가이드 표와 같다). 미리보기 재생 속도로 쓴다.
DEFAULT_FPS = {'idle': 2, 'walk': 6, 'sleep': 1, 'poked': 8, 'throw': 10, 'hit': 8, 'jump': 8,
               'eat': 6, 'wave': 6, 'happy': 4, 'offline': 1, 'fly': 12, 'impact': 12}


def rnd(v: float) -> int:
    """0.5 는 올림(JS Math.round). 파이썬 round 는 짝수 쪽으로 가서 좌우 포즈가 한 칸 어긋난다."""
    return math.floor(v + 0.5)


def in_ellipse(x: float, y: float, cx: float, cy: float, rx: float, ry: float) -> bool:
    """칸 (x, y) 의 가운데(+0.5)가 타원 안인가."""
    return ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1


def render(fill: Callable[[int, int], str]) -> Grid:
    grid = [[fill(x, y) for x in range(FRAME)] for y in range(FRAME)]

    def solid(x: int, y: int) -> bool:
        return 0 <= x < FRAME and 0 <= y < FRAME and grid[y][x] != '.'

    return [
        ''.join(
            ch if ch == '.' or (solid(x - 1, y) and solid(x + 1, y) and solid(x, y - 1) and solid(x, y + 1)) else 'K'
            for x, ch in enumerate(row)
        )
        for y, row in enumerate(grid)
    ]


def eye(x: float, y: float, ex: int, ey: int, kind: str, ink: str = 'E', hi: str = 'W') -> str | None:
    """눈 한쪽. (ex, ey) 는 3x3 눈 자리 왼쪽 위(정수로 넘긴다, 소수면 X·반달 눈이 안 그려진다).

    open: 3x3, 왼쪽 위 한 칸 하이라이트(hi) / closed: 아래로 볼록(잠) / happy: 위로 볼록(웃음)
    hurt: 5x5 X / wide: 4x4 + 하이라이트(놀람, 왼쪽 위로 한 칸 커진다)
    """
    dx, dy = x - ex, y - ey
    if kind == 'open':
        if dx < 0 or dx > 2 or dy < 0 or dy > 2:
            return None
        return hi if dx == 0 and dy == 0 else ink
    if kind == 'closed':
        return ink if (dy == 1 and dx in (-1, 3)) or (dy == 2 and 0 <= dx <= 2) else None
    if kind == 'happy':
        return ink if (dy == 0 and 0 <= dx <= 2) or (dy == 1 and dx in (-1, 3)) else None
    if kind == 'hurt':
        return ink if -1 <= dx <= 3 and -1 <= dy <= 3 and (dx == dy or dx == 2 - dy) else None
    if kind == 'wide':
        if dx < -1 or dx > 2 or dy < -1 or dy > 2:
            return None
        return hi if dx == -1 and dy == -1 else ink
    raise ValueError(f'모르는 눈 {kind}')


def seg(x: float, y: float, a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    """칸 가운데와 선분 a-b 사이 거리 d, 가장 가까운 점의 a 에서의 비율 t. 팔·막대를 그릴 때."""
    px, py = x + 0.5, y + 0.5
    (ax, ay), (bx, by) = a, b
    t = max(0.0, min(1.0, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))
    return math.hypot(px - (ax + t * (bx - ax)), py - (ay + t * (by - ay))), t


def in_tri(x: float, y: float, a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> bool:
    px, py = x + 0.5, y + 0.5

    def s(p: tuple[float, float], q: tuple[float, float]) -> float:
        return (px - q[0]) * (p[1] - q[1]) - (p[0] - q[0]) * (py - q[1])

    d = (s(a, b), s(b, c), s(c, a))
    return not (min(d) < 0 and max(d) > 0)


def spin(k: int, n: int, draw: Callable[[float, float], str]) -> Grid:
    """회전한 한 장(k/n 바퀴). 앱이 '날아갈 때 돌리기'로 돌리는 아이템엔 쓰지 않는다(겹쳐 돈다)."""
    a = (-k / n) * math.pi * 2
    c = FRAME / 2

    def fill(x: int, y: int) -> str:
        dx, dy = x + 0.5 - c, y + 0.5 - c
        return draw(c + dx * math.cos(a) - dy * math.sin(a) - 0.5, c + dx * math.sin(a) + dy * math.cos(a) - 0.5)

    return render(fill)


def diag(x: float, y: float) -> tuple[float, float]:
    """긴 물건(칼·봉)용 좌표: u 는 대각선 방향(0~FRAME), v 는 폭 방향(0 이 가운데)."""
    c = FRAME / 2
    dx, dy = x + 0.5 - c, y + 0.5 - c
    return c + (dx - dy) * math.sqrt(0.5), (dx + dy) * math.sqrt(0.5)


def tone(start: float, end: float, ms: int, noise: float) -> bytes:
    """8kHz 8bit 모노 효과음 wav. 주파수 start→end 로 미끄러지고 noise(0~1) 만큼 잡음을 섞는다."""
    rate = 8000
    n = rnd(rate * ms / 1000)
    out = bytearray(struct.pack('<4sI4s4sIHHIIHH4sI', b'RIFF', 36 + n, b'WAVE', b'fmt ', 16, 1, 1, rate, rate, 1, 8,
                                b'data', n))
    phase, r = 0.0, 1
    for i in range(n):
        t = i / n
        phase += 2 * math.pi * (start + (end - start) * t) / rate
        s = (1 - noise) * math.sin(phase) + noise * (r / 2**31 - 1)
        r = (r ^ (r << 13)) & 0xFFFFFFFF
        r ^= r >> 17
        r = (r ^ (r << 5)) & 0xFFFFFFFF
        out.append(128 + rnd(70 * s * (1 - t)))
    return bytes(out)


# 응가 3단 똬리 [cx, cy, rx, ry](위 단부터). 앱 기본 응가와 같다. 맨 아랫줄(47)에 닿고 폭 17·높이 12칸.
POOP_TIERS = [(23.5, 38.8, 3.4, 1.9), (23.5, 41.9, 5.8, 2.2), (23.5, 44.9, 8.1, 3.1)]
# 응가는 이 칸(아래 가운데 24x24) 안에 있어야 한다. 앱 창·메뉴가 이 칸만 잘라 보여 준다.
POOP_AREA = (12, 24, 35, 47)


def poop(body: str, shade: str, extra: Callable[[int, int, int], str | None] | None = None,
         cheek: str = 'P', no_tip: bool = False) -> Grid:
    """캐릭터 응가 한 장. 기본 응가 모양에 캐릭터 색(body·shade)과 특징 하나(extra)만 얹는다.

    extra(x, y, tier) 는 단·얼굴보다 먼저 칠한다(귀·부리 등). tier 는 0(위)~2(아래), 단 밖이면 -1.
    cheek='' 이면 볼 없음, no_tip 은 맨 위 꼭지 빼기(귀를 얹을 때). 눈·입은 'E', 볼은 cheek 글자.
    """
    def fill(x: int, y: int) -> str:
        tier = next((i for i, (cx, cy, rx, ry) in enumerate(POOP_TIERS) if in_ellipse(x, y, cx, cy, rx, ry)), -1)
        e = extra(x, y, tier) if extra else None
        if e:
            return e
        if not no_tip and tier < 0 and 22 <= x <= 24 and y == 36:
            return body
        if tier < 0:
            return '.'
        if y == 44 and x in (20, 26):
            return 'E'
        if cheek and y == 45 and x in (18, 19, 27, 28):
            return cheek
        if y == 45 and x in (22, 24):
            return 'E'
        if y == 46 and x == 23:
            return 'E'
        _, cy, _, ry = POOP_TIERS[tier]
        return shade if tier < 2 and y >= cy + ry - 1.1 else body

    return render(fill)


def strip(frames: list[Grid], colors: dict[str, str], scale: int = 1, gap: int = 0) -> Image.Image:
    """프레임을 가로로 이은 RGBA 이미지. scale 배로 키우고 칸 사이를 gap 만큼 띄운다(미리보기용)."""
    cell = FRAME * scale + gap
    img = Image.new('RGBA', (len(frames) * cell - gap, FRAME * scale), (0, 0, 0, 0))
    for i, grid in enumerate(frames):
        for y, line in enumerate(grid):
            for x, ch in enumerate(line):
                if ch == '.':
                    continue
                if ch not in colors:
                    raise ValueError(f"색이 없는 글자 '{ch}'")
                n = int(colors[ch][1:], 16)
                rgba = ((n >> 16) & 255, (n >> 8) & 255, n & 255, 255)
                img.paste(rgba, (i * cell + x * scale, y * scale, i * cell + (x + 1) * scale, (y + 1) * scale))
    return img


def save_all(name: str, colors: dict[str, str], character: dict[str, list[Grid]],
             items: dict[str, dict] | None = None, out: str | Path = 'out', note: str = '') -> Path:
    """앱 '한꺼번에 넣기(.zip)' 가 읽는 모양으로 저장한다.

    items: {아이템 이름: {'kind': 'poop'|'throw'|'food', 'anims': {'fly': [...], 'impact': [...]}, 'sound': wav bytes}}
    결과: out/<이름>/<동작>.png(올릴 1배 파일), out/<이름>.zip, out/preview/<이름>-<동작>.png(8배 확인용).
    zip 하나 = 만들기 창 항목 하나(캐릭터 하나, 아이템 하나).
    note: 후보 고르기 카드(gallery.py --pick)에 쓸 특징 한 줄.
    """
    out = Path(out)
    (out / 'preview').mkdir(parents=True, exist_ok=True)
    entries = [(name, 'character', character, None)]
    entries += [(k, v['kind'], v['anims'], v.get('sound')) for k, v in (items or {}).items()]
    kinds = {'character': '캐릭터 탭', 'poop': '아이템 탭, 종류 응가', 'throw': '아이템 탭, 종류 던질 것',
             'food': '아이템 탭, 종류 먹이'}
    for folder, kind, anims, sound in entries:
        d = out / folder
        d.mkdir(parents=True, exist_ok=True)
        # validate 가 응가를 이름이 아니라 종류로 알게 둔다(점 파일은 zip·앱이 안 읽는다).
        (d / '.kind').write_text(kind)
        if kind == 'character' and note:
            (d / '.note').write_text(note)
        with zipfile.ZipFile(out / f'{folder}.zip', 'w', zipfile.ZIP_DEFLATED) as z:
            for anim, frames in anims.items():
                buf = io.BytesIO()
                strip(frames, colors).save(buf, 'PNG', optimize=True)
                (d / f'{anim}.png').write_bytes(buf.getvalue())
                z.writestr(f'{anim}.png', buf.getvalue())
                strip(frames, colors, 8, 8).save(out / 'preview' / f'{folder}-{anim}.png')
            if sound:
                (d / 'sound.wav').write_bytes(sound)
                z.writestr('sound.wav', sound)
        print(f'{out / folder}.zip  ({kinds[kind]})')
    return out
