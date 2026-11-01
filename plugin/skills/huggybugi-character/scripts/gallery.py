"""출력 폴더의 모든 캐릭터·아이템 동작을 한 페이지에 움직이게 모은다(3배 + 실제 크기).

사용: python3 gallery.py <출력 폴더> [<다른 출력 폴더> ...]
결과: <첫 출력 폴더>/gallery.html (브라우저로 연다), <첫 출력 폴더>/sheet.png (모든 프레임을 한 장에, 이미지만 볼 수 있을 때)
후보를 비교할 땐 안마다 다른 폴더로 그려 여기 같이 넘긴다.
후보 고르기 카드: python3 gallery.py --pick <출력 폴더> [...] → pick.html, pick.png (idle 한 장씩)
"""

import html
import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit('Pillow 가 없어요. 먼저 설치하세요: python3 -m pip install pillow')

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import CHARACTER_ANIMS, DEFAULT_FPS, FRAME, ITEM_ANIMS  # noqa: E402



def pick(outs: list[Path]) -> None:
    """후보 고르기: 캐릭터마다 idle 첫 장을 6배·실제 크기 카드로. <폴더>/.note 가 있으면 특징 한 줄로 쓴다."""
    page = outs[0] / 'pick.html'
    cards, imgs = [], []
    for out in outs:
        for d in sorted(p for p in out.iterdir() if (p / 'idle.png').exists()):
            strip = Image.open(d / 'idle.png').convert('RGBA')
            n = strip.width // FRAME
            idle = strip.crop((0, 0, FRAME, FRAME))
            imgs.append(idle)
            url = html.escape(os.path.relpath(d / 'idle.png', page.parent).replace(os.sep, '/'))
            note = (d / '.note').read_text().strip() if (d / '.note').exists() else ''
            cards.append(f'<figure><div class="g" style="background-image:url(\'{url}\');background-size:{n * FRAME * 6}px {FRAME * 6}px"></div>'
                         f'<div class="d"><div style="background-image:url(\'{url}\')"></div></div>'
                         f'<figcaption><b>{len(cards) + 1}. {html.escape(d.name)}</b><br>{html.escape(note)}</figcaption></figure>')
    big = FRAME * 6
    page.write_text(f'''<!doctype html><meta charset="utf-8"><title>허기부기 캐릭터 후보</title><style>
body{{font-family:-apple-system,sans-serif;background:#1d1a24;color:#eee;margin:24px}} p{{color:#aaa;font-size:13px}}
.wrap{{display:grid;grid-template-columns:repeat(auto-fill,{big + 24}px);gap:16px}}
figure{{margin:0;background:#2a2633;border-radius:10px;padding:12px}}
.g{{width:{big}px;height:{big}px;image-rendering:pixelated;background-repeat:no-repeat;
background-color:#332f3d;border-radius:6px}}
.d{{background:#7aa0c8;border-radius:6px;margin-top:8px;padding:4px 8px;height:{FRAME}px}}
.d div{{width:{FRAME}px;height:{FRAME}px;image-rendering:pixelated;background-repeat:no-repeat}}
figcaption{{font-size:13px;margin-top:8px;line-height:1.5}}
</style><p>위: 6배 / 아래: 실제 크기(바탕화면 위). 번호로 골라 주세요.</p><div class="wrap">{"".join(cards)}</div>''', encoding='utf-8')
    # 이미지만 볼 수 있을 때: idle 을 6배로 나란히(기본 글꼴은 한글을 못 그려 번호만)
    sheet = Image.new('RGBA', (max(1, len(imgs)) * (big + 12), big + 30), (42, 38, 51, 255))
    draw = ImageDraw.Draw(sheet)
    for i, im in enumerate(imgs):
        sheet.alpha_composite(im.resize((big, big), Image.NEAREST), (i * (big + 12) + 6, 6))
        draw.text((i * (big + 12) + 6, big + 12), str(i + 1), fill=(220, 220, 220, 255))
    sheet.save(outs[0] / 'pick.png')
    print(page)
    print(outs[0] / 'pick.png')


if sys.argv[1:2] == ['--pick']:
    if len(sys.argv) < 3:
        sys.exit('사용: python3 gallery.py --pick <출력 폴더> [...]')
    pick([Path(p).resolve() for p in sys.argv[2:]])
    sys.exit(0)

S = 3
outs = [Path(p).resolve() for p in sys.argv[1:]]
if not outs:
    sys.exit('사용: python3 gallery.py <출력 폴더> [...]')
page = outs[0] / 'gallery.html'

rows, sheet_rows, folders = [], [], []
for out in outs:
    for d in sorted((p for p in out.iterdir() if p.is_dir() and p.name != 'preview'),
                    key=lambda p: (not (p / 'idle.png').exists(), p.name)):  # 캐릭터 먼저
        folders.append(d)
        anims = CHARACTER_ANIMS if (d / 'idle.png').exists() else ITEM_ANIMS
        # 아이템 impact 는 선택이라 없으면 칸을 안 만든다(응가·먹이는 보통 fly 만).
        if anims is ITEM_ANIMS:
            anims = [a for a in anims if (d / f'{a}.png').exists()]
        tds = []
        for a in anims:
            src = d / f'{a}.png'
            if not src.exists():
                tds.append(f'<td class="miss">{a}<br>없음</td>')
                continue
            img = Image.open(src)
            n = img.width // FRAME
            sheet_rows.append((f'{len(folders)}. {a}', img.convert('RGBA')))  # 기본 글꼴은 한글을 못 그려 번호로
            url = html.escape(os.path.relpath(src, page.parent).replace(os.sep, '/'))
            anim = f'animation-timing-function:steps({n});animation-duration:{n / DEFAULT_FPS[a]}s'
            tds.append(f'<td><div class="sp" style="background-image:url(\'{url}\');background-size:{n * FRAME * S}px {FRAME * S}px;'
                       f'--w:-{n * FRAME * S}px;{anim}"></div><div class="real" style="background-image:url(\'{url}\');'
                       f'--w:-{n * FRAME}px;{anim}"></div>{a} · {n}장</td>')
        label = html.escape(d.name if len(outs) == 1 else f'{out.name}/{d.name}')
        rows.append(f'<tr><th>{label}</th>{"".join(tds)}</tr>')

page.write_text(f'''<!doctype html><meta charset="utf-8"><title>허기부기 캐릭터 미리보기</title><style>
body{{font-family:-apple-system,sans-serif;background:#1d1a24;color:#ddd;margin:20px;font-size:12px}}
table{{border-collapse:separate;border-spacing:6px}} th{{font-size:14px;text-align:left;padding-right:8px;white-space:nowrap}}
td{{background:#2a2633;border-radius:8px;padding:6px;text-align:center;vertical-align:top}} td.miss{{color:#776;width:{FRAME * S}px}}
.sp{{width:{FRAME * S}px;height:{FRAME * S}px;image-rendering:pixelated;background-repeat:no-repeat;background-color:#332f3d;border-radius:4px;animation-name:play;animation-iteration-count:infinite}}
.real{{width:{FRAME}px;height:{FRAME}px;image-rendering:pixelated;background-repeat:no-repeat;margin:4px auto;background-color:#7aa0c8;border-radius:4px;animation-name:play;animation-iteration-count:infinite}}
@keyframes play{{to{{background-position:var(--w) 0}}}}
</style><p>위: 3배, 아래: 실제 크기(파란 바탕)</p><table>{"".join(rows)}</table>''', encoding='utf-8')

# 정지 시트: 줄마다 동작 하나, 프레임을 3배로 나란히
cell = FRAME * S + 6
sheet = Image.new('RGBA', (180 + 8 * cell, max(1, len(sheet_rows)) * cell), (42, 38, 51, 255))
draw = ImageDraw.Draw(sheet)
for r, (label, img) in enumerate(sheet_rows):
    draw.text((6, r * cell + cell // 2 - 6), label, fill=(220, 220, 220, 255))
    for k in range(img.width // FRAME):
        fr = img.crop((k * FRAME, 0, (k + 1) * FRAME, FRAME)).resize((FRAME * S, FRAME * S), Image.NEAREST)
        x, y = 180 + k * cell, r * cell + 3
        draw.rectangle((x, y, x + FRAME * S - 1, y + FRAME * S - 1), fill=(51, 47, 61, 255))
        sheet.alpha_composite(fr, (x, y))
sheet.save(outs[0] / 'sheet.png')
print(page)
print(outs[0] / 'sheet.png', ' '.join(f'{i}={d.name}' for i, d in enumerate(folders, 1)))
