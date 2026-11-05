"""떠기(회색 펭귄 인형, 앱 사용 안내의 예시 캐릭터): 11개 동작 + 떠기 응가 + 던질 것 눈뭉치.

실행: python3 examples/ddeogi/make.py [출력 폴더]   (기본 out)
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from lib import TURN, eye, in_ellipse, in_tri, poop, render, rnd, save_all, tone  # noqa: E402

COLORS = {
    'K': '#3a3640',
    'G': '#9a98a3',  # 몸
    'g': '#7f7d88',  # 날개·응가 그늘
    'W': '#fbf9f4',  # 얼굴·배
    'Y': '#f7c535',  # 부리·발
    'y': '#e2a51f',
    'E': '#2a1c18',
    'P': '#ffb3c0',
    'R': '#e8586a',
    'B': '#cfe4f5',  # 눈뭉치
    'b': '#9ec4e6',
}

# 치수는 32칸으로 정한 값을 48칸으로 옮긴 것이라 S 를 곱한다. 새 캐릭터는 처음부터 48칸으로 정하면 된다.
S = 1.5


def u(v):
    """포즈 이동량을 48칸 정수로. 부호를 떼고 반올림해야 좌우 포즈가 대칭이다."""
    return int(math.copysign(rnd(abs(v) * S), v)) if v else 0


def draw(bob=0, squash=0, feet=(0, 0), flip=(0, 0), eyes='open', mouth='none', blush=False, lean=0):
    """bob: + 앉음 - 뜀 / squash: + 납작 - 길쭉(발은 그대로) / feet: 발 들기 / flip: 날개 높이 / lean: 몸 좌우."""
    ry = (9 - squash) * S
    # 눌린 몸·기운 몸·날개가 48칸 밖으로 나가지 않게 가둔다.
    rx = min((13 + squash * 0.8) * S, 22.4)
    by = (30.4 + min(bob, 1)) * S - ry + max(bob - 1, 0) * S
    cx = min(max((16 + lean) * S, rx + 1.4), 46.6 - rx)
    wl = max(cx - rx + 0.3 * S, 4.5)
    wr = min(cx + rx - 0.3 * S, 43.5)
    fy = by + 1.5 * S
    ey = rnd(by - 3 * S)
    shift = TURN + u(lean)  # 얼굴은 TURN 만큼 오른쪽, 몸이 기울면 같이 간다
    # 발을 몸보다 앞에 칠하기 시작하는 줄(그 위는 몸이 가린다)
    gy = rnd((30 + min(bob, 0)) * S) - u(max(feet))

    def foot(fcx, x, y, up):
        # 위 두 줄 9칸, 맨 아랫줄 6칸. 몸이 내려앉으면(bob<0) 몸까지 닿게 위로 늘인다.
        b = 47 - u(up)
        return b - 2 + min(0, u(bob + up)) <= y <= b and abs(x + 0.5 - fcx) <= (3.5 if y == b else 4.8)

    def fill(x, y):
        body = in_ellipse(x, y, cx, by, rx, ry) or in_tri(
            x, y, (cx - 3.5 * S, by - ry + 2 * S), (cx + 3.5 * S, by - ry + 2 * S), (cx, by - ry - 0.8 * S))
        fin = (in_ellipse(x, y, wl, fy - flip[0] * S, 2.6 * S, 1.8 * S)
               or in_ellipse(x, y, wr, fy - flip[1] * S, 2.6 * S, 1.8 * S))
        paw = foot(18.5, x, y, feet[0]) or foot(31.5, x, y, feet[1])
        # 인형처럼 발이 몸 앞으로 나와 보이게 몸보다 먼저 칠한다
        if paw and y >= gy:
            return 'Y'
        if not body:
            return 'g' if fin else 'Y' if paw else '.'
        fx = x - shift
        e = eye(fx, y, 14, ey, eyes) or eye(fx, y, 31, ey, eyes)
        if e:
            return e
        # 부리: 위 두 줄 6칸, 아랫줄 4칸. 먹을 땐 사이가 벌어져 입속이 보인다
        if y in (ey + 2, ey + 3) and 21 <= fx <= 26:
            return 'Y'
        if mouth == 'open':
            if ey + 4 <= y <= ey + 5 and 22 <= fx <= 25:
                return 'R'
            if y == ey + 6 and 22 <= fx <= 25:
                return 'Y'
        elif y == ey + 4 and (21 if mouth == 'chew' else 22) <= fx <= (26 if mouth == 'chew' else 25):
            return 'y'
        if blush and y in (ey + 3, ey + 4) and (11 <= fx <= 13 or 34 <= fx <= 36):
            return 'P'
        face = (in_ellipse(fx, y, 11 * S + 0.5, by - 2 * S, 3.8 * S, 3.6 * S)
                or in_ellipse(fx, y, 21 * S + 0.5, by - 2 * S, 3.8 * S, 3.6 * S)
                or in_ellipse(fx, y, 16 * S + 0.5, by + 3 * S, 8.2 * S, 5.2 * S))
        return 'W' if face else 'G'

    return render(fill)


f = draw

CHARACTER = {
    'idle': [f(), f(bob=1)],
    'walk': [f(feet=(1, 0), lean=-1), f(bob=-1), f(feet=(0, 1), lean=1), f(bob=-1)],
    'sleep': [f(eyes='closed', bob=1, squash=1), f(eyes='closed', bob=2, squash=1)],
    'poked': [f(eyes='wide', squash=3), f(eyes='wide')],
    'throw': [f(flip=(0, 4), lean=-1), f(flip=(0, 5), lean=-1, bob=-1), f(flip=(0, -1), lean=1)],
    'hit': [f(eyes='hurt', lean=-2, squash=1), f(eyes='hurt', bob=1)],
    'jump': [f(squash=3, flip=(-1, -1)), f(bob=-3, squash=-1, feet=(2, 2), flip=(3, 3))],
    'eat': [f(mouth='open'), f(mouth='chew', bob=1, squash=1), f(eyes='happy', blush=True)],
    'wave': [f(flip=(0, 3), eyes='happy'), f(flip=(0, 6), eyes='happy'), f(flip=(0, 3), eyes='happy')],
    'happy': [f(eyes='happy', blush=True, bob=-1), f(eyes='happy', blush=True)],
    'offline': [f(eyes='hurt', squash=3, bob=1, flip=(-1, -1))],  # 납작하게 쓰러진 X 눈
}


# 응가: 회색 소용돌이, 아래 단에 흰 배와 노란 부리(특징 하나)
def ddeogi_poop_extra(x, y, t):
    if t == 2 and 45 <= y <= 46 and 22 <= x <= 24:
        return 'Y'
    if t == 2 and in_ellipse(x, y, 23.5, 46.5, 3.8, 2.2):
        return 'W'
    return None


# 던질 것: 눈뭉치 한 장(앱이 돌린다) + 흩어지는 조각 3장
def snowball(x, y):
    if not in_ellipse(x, y, 24, 24, 9.75, 9.75):
        return '.'
    if in_ellipse(x, y, 20.25, 20.25, 2.1, 2.1):
        return 'W'
    if in_ellipse(x, y, 27, 27.75, 1.8, 1.5):
        return 'b'
    return 'W' if in_ellipse(x, y, 22.5, 22.5, 8.1, 8.1) else 'B'


def burst(k):
    def fill(x, y):
        r, s = 8 + k * 5.5, 3.9 - k * 0.75  # 48칸 가장자리에 닿지 않는 반지름
        for i in range(6):
            a = i / 6 * math.pi * 2 + k * 0.2
            if in_ellipse(x, y, 24 + math.cos(a) * r, 24 + math.sin(a) * r, s, s):
                return 'B' if k == 2 else 'W'
        return '.'

    return render(fill)


if __name__ == '__main__':
    save_all(
        name='떠기',
        colors=COLORS,
        character=CHARACTER,
        items={
            '떠기 응가': {'kind': 'poop', 'anims': {'fly': [poop(body='G', shade='g', extra=ddeogi_poop_extra)]}},
            '눈뭉치': {'kind': 'throw', 'anims': {'fly': [render(snowball)], 'impact': [burst(k) for k in range(3)]},
                     'sound': tone(260, 110, 140, 0.8)},
        },
        out=sys.argv[1] if len(sys.argv) > 1 else 'out',
    )
