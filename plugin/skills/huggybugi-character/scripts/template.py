"""새 캐릭터 시작점. 작업 폴더로 복사해 COLORS·draw·CHARACTER·응가를 고친다.

실행: python3 make.py [출력 폴더]   (기본 out)
lib.py 는 이 파일 옆, 또는 SKILL.md 옆 scripts/ 에서 찾는다. 다른 곳이면 HB_LIB 에 scripts 폴더 경로를 준다.
"""

import math
import os
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path[:0] = [p for p in (os.environ.get('HB_LIB'), str(_here), str(_here.parent / 'scripts'), str(_here.parents[1] / 'scripts')) if p]
from lib import TURN, eye, in_ellipse, poop, render, rnd, save_all, seg, tone  # noqa: E402

COLORS = {
    'K': '#3a3640',  # 외곽선(render 가 가장자리를 자동으로 K 로)
    'B': '#d3cdc4',  # 몸
    'b': '#bdb5aa',  # 몸 그늘
    'W': '#fbfaf6',
    'E': '#1c1a1a',  # 눈·입
    'P': '#f7b0b8',  # 볼
    'R': '#e8586a',
    'Y': '#ffd84a',
    'y': '#d9a91c',
}


def draw(bob=0, squash=0, feet=(0, 0), arm=(0, 0), eyes='open', mouth='w', lean=0):
    """포즈 값만 받아 한 장. 모든 동작이 이 함수 하나를 써서 모양이 어긋나지 않는다.

    bob: + 아래로(앉음) - 위로(뜀) / squash: + 납작 - 길쭉 / feet: 발 들기 / arm: 팔 들기(0 이면 숨김)
    eyes: open closed happy hurt wide / mouth: w open chew / lean: 몸 좌우
    """
    cx = 24 + lean
    lift = min(bob, 0)
    ry = 15 - squash
    by = 44.5 + lift + max(bob - 2, 0) - ry  # 몸 바닥을 발 위에 붙인다
    ey = rnd(by - 3)

    def fill(x, y):
        # 칠하는 순서 = 앞뒤 순서. 먼저 검사한 것이 앞에 보인다.
        for i, side in enumerate((-1, 1)):
            if arm[i] > 0 and seg(x, y, (cx + side * 13.5, by), (cx + side * 18, by - arm[i]))[0] < 2.25:
                return 'B'

        def foot(fx, up):
            return in_ellipse(x, y, fx, 45.5 + lift - up, 3.9, 2.4)

        if y >= 42 + lift and (foot(cx - 6, feet[0]) or foot(cx + 6, feet[1])):
            return 'b'
        if not in_ellipse(x, y, cx, by, 16.5 + squash * 0.7, ry):
            return '.'
        fx = x - TURN - lean  # 얼굴만 오른쪽으로
        e = eye(fx, y, 17, ey, eyes) or eye(fx, y, 29, ey, eyes)
        if e:
            return e
        if y in (ey + 3, ey + 4) and (12 <= fx <= 14 or 34 <= fx <= 36):
            return 'P'
        my = ey + 5
        if mouth == 'open' and my <= y <= my + 2 and 22 <= fx <= 26:
            return 'E' if y == my or fx in (22, 26) else 'R'
        if mouth == 'chew' and y == my + 1 and 21 <= fx <= 27:
            return 'E'
        # 7칸 2줄 지그재그 w
        if mouth == 'w' and ((y == my and fx in (21, 24, 27)) or (y == my + 1 and 22 <= fx <= 26 and fx != 24)):
            return 'E'
        return 'b' if y > by + ry - 4.5 else 'B'

    return render(fill)


f = draw

CHARACTER = {
    'idle': [f(), f(bob=2)],
    'walk': [f(feet=(2, 0), lean=-2), f(bob=-2), f(feet=(0, 2), lean=2), f(bob=-2)],
    'sleep': [f(eyes='closed', bob=2, squash=1.5), f(eyes='closed', bob=3, squash=2.5)],
    'poked': [f(eyes='wide', squash=4), f(eyes='wide')],
    'throw': [f(arm=(0, 5), lean=-2), f(arm=(0, 8), lean=-2, bob=-2), f(arm=(0, 2), lean=2)],
    'hit': [f(eyes='hurt', lean=-2, squash=1.5), f(eyes='hurt', bob=2)],
    'jump': [f(squash=4), f(bob=-4, squash=-1.5, feet=(3, 3), arm=(5, 5))],
    'eat': [f(mouth='open', arm=(3, 3)), f(mouth='chew', bob=2, squash=1.5), f(eyes='happy')],
    'wave': [f(arm=(0, 6), eyes='happy'), f(arm=(0, 9), eyes='happy'), f(arm=(0, 6), eyes='happy')],
    'happy': [f(eyes='happy', bob=-2), f(eyes='happy')],
    'offline': [f(eyes='hurt', squash=4, bob=2)],  # 오프라인: 납작하게 쓰러진 X 눈
}

# 던질 것 예시: 공 + 터지는 조각. 앱이 날아가는 동안 돌리니 fly 는 한 장(회전 프레임 금지, 겹쳐 돈다).
ball = [render(lambda x, y: '.' if not in_ellipse(x, y, 24, 24, 9, 9)
               else 'W' if in_ellipse(x, y, 21, 21, 2.1, 2.1) else 'Y')]


def pop(k):
    def fill(x, y):
        for i in range(6):
            a = i / 6 * math.pi * 2 + k * 0.3
            r = 9 + k * 6
            if in_ellipse(x, y, 24 + math.cos(a) * r, 24 + math.sin(a) * r, 3.3 - k * 0.75, 3.3 - k * 0.75):
                return 'Y'
        return '.'

    return render(fill)


if __name__ == '__main__':
    save_all(
        name='템플릿',
        colors=COLORS,
        character=CHARACTER,
        items={
            # 기본 세트: 이 캐릭터 응가. 몸 색과 특징 하나만 얹는다(여기선 볼).
            '템플릿 응가': {'kind': 'poop', 'anims': {'fly': [poop(body='B', shade='b')]}},
            # 던질 것·먹이는 사용자가 원할 때만
            '공': {'kind': 'throw', 'anims': {'fly': ball, 'impact': [pop(k) for k in range(3)]},
                  'sound': tone(600, 250, 120, 0.3)},
        },
        out=sys.argv[1] if len(sys.argv) > 1 else 'out',
    )
