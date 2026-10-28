"""출력 폴더를 앱 만들기 창과 같은 규칙으로 검사한다. 사용: python3 validate.py <출력 폴더>

문제(앱이 거절): 크기·칸 수·모서리·동작 이름·필수 동작·wav.
주의(올라가지만 확인): 위·옆 가장자리 닿음(잘림), 캐릭터가 작음, 응가가 아래 가운데 24x24 밖.
"""

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit('Pillow 가 없어요. 먼저 설치하세요: python3 -m pip install pillow')

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import CHARACTER_ANIMS, FRAME, ITEM_ANIMS, POOP_AREA  # noqa: E402

MAX_PNG = 200 * 1024
MAX_WAV = 50 * 1024
MAX_FRAMES = 8
# 만들기 창 템플릿 선 색(RGBA). 템플릿 레이어를 안 끄고 저장한 그림을 막는다.
TEMPLATE = [(60, 60, 70, 200), (120, 120, 130, 70), (255, 90, 90, 160)]


def check_png(path: Path, frames_ok: int = MAX_FRAMES) -> tuple[str | None, Image.Image | None]:
    data = path.read_bytes()
    if len(data) > MAX_PNG:
        return '200KB 넘음', None
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return 'PNG 아님', None
    img = Image.open(path).convert('RGBA')
    w, h = img.size
    if h != FRAME:
        return f'높이 {h}, {FRAME} 이어야 함', None
    if w == 0 or w % FRAME:
        return f'가로 {w}, {FRAME} 의 배수여야 함', None
    if w // FRAME > frames_ok:
        return f'{w // FRAME}칸, {frames_ok}칸까지', None
    px = img.load()
    for y in range(h):
        for x in range(w):
            p = px[x, y]
            if any(p[3] == c[3] and all(abs(p[i] - c[i]) <= 6 for i in range(3)) for c in TEMPLATE):
                return '템플릿 선이 남음', None
    last = FRAME - 1
    for k in range(w // FRAME):
        if all(px[k * FRAME + x, y][3] for x, y in ((0, 0), (last, 0), (0, last), (last, last))):
            return f'{k}번 칸 네 모서리가 다 칠해짐(배경이 안 지워짐)', None
    return None, img


def frames_of(img: Image.Image):
    return [img.crop((k * FRAME, 0, (k + 1) * FRAME, FRAME)) for k in range(img.width // FRAME)]


def main(out: Path) -> int:
    bad, warn = [], []
    for d in sorted(p for p in out.iterdir() if p.is_dir() and p.name != 'preview'):
        files = sorted(p.name for p in d.iterdir() if not p.name.startswith('.'))
        is_char = 'idle.png' in files
        allowed = CHARACTER_ANIMS if is_char else ITEM_ANIMS
        for f in files:
            path = d / f
            if f == 'sound.wav' and not is_char:
                data = path.read_bytes()
                if len(data) > MAX_WAV:
                    bad.append(f'{d.name}/{f}: 50KB 넘음')
                elif data[:4] != b'RIFF' or data[8:12] != b'WAVE':
                    bad.append(f'{d.name}/{f}: wav 아님')
                continue
            if not f.endswith('.png') or f[:-4] not in allowed:
                bad.append(f'{d.name}/{f}: 앱이 모르는 파일 이름({", ".join(allowed)}' + ('' if is_char else ', sound.wav') + ')')
                continue
            problem, img = check_png(path)
            if problem:
                bad.append(f'{d.name}/{f}: {problem}')
                continue
            for k, fr in enumerate(frames_of(img)):
                a = fr.getchannel('A')
                if any(a.getpixel((i, 0)) or a.getpixel((0, i)) or a.getpixel((FRAME - 1, i)) for i in range(FRAME)):
                    warn.append(f'{d.name}/{f} {k}번 칸: 위·옆 가장자리에 닿음(잘렸는지 확인)')
                bbox = a.getbbox()
                if not bbox:
                    warn.append(f'{d.name}/{f} {k}번 칸: 비어 있음')
        need = ['idle', 'walk', 'sleep'] if is_char else ['fly']
        for n in need:
            if f'{n}.png' not in files:
                bad.append(f'{d.name}: 필수 동작 {n} 없음')
        if is_char and 'offline.png' not in files:
            warn.append(f'{d.name}: offline 없음(오프라인 때 돌로 보임)')
        if is_char and 'idle.png' in files and not check_png(d / 'idle.png')[0]:
            first = frames_of(Image.open(d / 'idle.png').convert('RGBA'))[0].getchannel('A')
            l, t, r, b = first.getbbox() or (0, 0, 0, 0)
            filled = FRAME * FRAME - first.histogram()[0]
            print(f'{d.name} idle 크기: 높이 {b - t}칸, 칠한 칸 {filled}')
            if filled < 700:
                warn.append(f'{d.name}: idle 이 작음(칠한 칸 800~1200 권장, 앱은 키우지 않아 다른 캐릭터 옆에서 작아 보인다)')
            if b != FRAME:
                warn.append(f'{d.name}: idle 발이 맨 아랫줄({FRAME - 1})에 안 닿음')
        if len(d.name) > 20:
            bad.append(f'{d.name}: 이름이 20자 넘음(앱이 저장을 거절)')
        kind = (d / '.kind').read_text().strip() if (d / '.kind').exists() else ''
        if (kind == 'poop' or d.name.endswith('응가')) and 'fly.png' in files and not check_png(d / 'fly.png')[0]:
            img = Image.open(d / 'fly.png').convert('RGBA')
            box = img.getchannel('A').getbbox()
            x0, y0, x1, y1 = POOP_AREA
            if img.width != FRAME:
                bad.append(f'{d.name}/fly.png: 응가는 한 장')
            elif box and not (box[0] >= x0 and box[1] >= y0 and box[2] <= x1 + 1 and box[3] <= y1 + 1):
                warn.append(f'{d.name}: 아래 가운데 24x24(x {x0}~{x1}, y {y0}~{y1}) 밖으로 나감 {box}')
            elif box and box[3] != FRAME:
                warn.append(f'{d.name}: 맨 아랫줄에 안 닿음(떠 보인다)')
    for b in bad:
        print(b)
    for w in warn:
        print(f'주의 {w}')
    print(f'문제 {len(bad)}개' if bad else 'all ok')
    return 1 if bad else 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('사용: python3 validate.py <출력 폴더>')
    sys.exit(main(Path(sys.argv[1])))
