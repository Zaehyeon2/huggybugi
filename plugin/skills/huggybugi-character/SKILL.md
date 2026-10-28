---
name: huggybugi-character
description: 허기부기(Huggybugi) 데스크톱 펫 앱에 올릴 48px 픽셀 캐릭터·아이템을 사진·그림·이름에서 파이썬 코드로 그려 동작별 PNG 스트립과 '한꺼번에 넣기(.zip)'용 zip 으로 만든다. "이 사진으로 허기부기 캐릭터 만들어줘", "내 고양이/인형으로 캐릭터 그려줘", "허기부기 캐릭터·응가·던질 것·먹이 만들어줘", "48px 펫 스프라이트", "만든 캐릭터 눈·다리·색 고쳐줘", "동작 하나 더 그려줘" 같은 요청이면 쓴다.
---

# 허기부기 캐릭터 만들기

사진·그림·이름을 보고 캐릭터를 **코드로** 그린다(이미지 생성 모델은 48칸을 못 지킨다). 결과는 동작마다 PNG 한 장과, 앱 만들기 창 "한꺼번에 넣기(.zip)"에 바로 넣는 zip. 올리기는 사용자가 앱에서 직접 한다.

필요한 것: 코드를 실행할 수 있는 환경, Python 3.10+, Pillow(`pip install pillow`). 아래 `${CLAUDE_SKILL_DIR}` 는 이 파일이 있는 폴더다(Claude Code 는 알아서 바꿔 준다. 다른 곳에서는 이 SKILL.md 위치를 기준으로 절대 경로로 바꿔 쓴다).

- `scripts/lib.py`: 그리기 도구(`render`·`in_ellipse`·`eye`·`seg`·`in_tri`·`poop`·`tone`·`save_all`)
- `scripts/template.py`: 새 캐릭터 시작점 / `examples/ddeogi/make.py`: 다 만든 예시(펭귄 떠기)
- `scripts/validate.py`: 앱 규칙 검사 / `scripts/gallery.py`: 움직이는 미리보기 페이지·한 장 시트
- `references/drawing.md`: 규격과 48칸 그리기 함정. **그리기 전에 읽는다.**

## 1. 정하기

레퍼런스를 보고 특징(체형·비율·색·귀·눈·볼·입·꼬리·소품)을 짧게 말로 정리해 사용자에게 보인다. 모르는 것만 묻는다(묻기 도구가 있으면 그걸로, 한 번에 몇 개만).

- 캐릭터 이름(17자까지. 응가도 만들면 `<이름> 응가` 가 앱 상한 20자 안이어야 한다)
- 응가·던질 것·먹이도 만들지(한 번에 묻는다). 던질 것이면 날아갈 때 돌릴지(공·돌), 가는 쪽을 보고 똑바로 갈지(화살·발톱)

**모습(묻지 않는다):** 정면에 얼굴만 살짝 오른쪽(`TURN`). 레퍼런스가 옆모습이어도 정면으로 바꿔 그린다. 사용자가 옆모습을 달라고 할 때만 옆.

**기본 세트(묻지 않고 만든다):** 캐릭터 11개 동작(idle walk sleep poked throw hit jump eat wave happy offline). 응가(`<이름> 응가`)·던질 것·먹이는 위에서 원한다고 한 것만.

레퍼런스가 없으면 실제 동물은 그 동물 비율대로 그리고, 애매하면 체형을 한 줄로 정리해 묻는다. 남의 저작권 캐릭터는 개인적으로만 쓰도록 안내한다.

## 2. 그리기

`scripts/template.py` 를 작업 폴더의 `make.py` 로 복사해 고친다(lib.py 를 못 찾으면 `HB_LIB=${CLAUDE_SKILL_DIR}/scripts`).

- **포즈 함수 하나** `draw(bob, squash, feet, arm, eyes, mouth, lean, ...)` 가 몸·얼굴 도형을 정의하고, `CHARACTER` 의 11개 동작은 포즈 값만 바꿔 부른다. 동작끼리 모양이 어긋나지 않는다.
- 도형은 타원(`in_ellipse`)·삼각형(`in_tri`)·선분(`seg`)으로. 칸 가운데(+0.5) 기준이다. 외곽선은 `render` 가 자동으로 그린다(글자 `K`).
- `COLORS` 글자 하나 = 색 하나. 8~12색이면 충분하다.
- 응가(원할 때만)는 `poop(body=몸색, shade=그늘색, extra=특징 하나)`. 예시는 `examples/ddeogi/make.py`.
- 던질 것은 fly 한 장 + impact 3장(+ `tone()` 효과음), 먹이는 똑바로 선 fly 1~4장. 원할 때만.
- `save_all(name, colors, character, items, out)` 이 파일·zip·미리보기를 쓴다.

```bash
python3 make.py out                       # out/<이름>/*.png, out/<이름>.zip, out/preview/*.png
python3 ${CLAUDE_SKILL_DIR}/scripts/validate.py out    # 'all ok' 가 나와야 한다
python3 ${CLAUDE_SKILL_DIR}/scripts/gallery.py out     # out/gallery.html(움직임), out/sheet.png(한 장)
```

## 3. 보여 주고 고치기

- `out/sheet.png` 나 `out/preview/<이름>-<동작>.png`(8배)를 **직접 열어 본다**. 적어도 idle·walk·wave·happy·offline. 이상한 점은 `references/drawing.md` 의 부위별 항목과 대조해 먼저 고친다.
- 처음엔 **idle 한 장만** 그려 보여 주고 모양(체형·눈·입·색)을 먼저 맞춘다. 안이 여럿이면(체형·색 후보, 여러 캐릭터) 안마다 다른 폴더로 그리고 `save_all(..., note='특징 한 줄')` 로 저장한 뒤 `gallery.py --pick <폴더> ...` 로 번호 카드 한 페이지(`pick.html`, 이미지만 되면 `pick.png`)를 보여 주고 번호로 고르게 한다. 사용자가 좋다고 하면 나머지 동작을 그린다.
- 고칠 때는 `draw` 의 도형·포즈 값만 바꾸고 다시 실행 → validate → 미리보기. 고치는 건 여러 번 왕복하는 게 정상이다.
- 승인은 두 번 받는다. ① idle 한 장 모양 ② 11개 동작 전체. 11개를 다 그리면 zip 은 주지 말고 동작 표만 보여 준다(브라우저를 쓸 수 있으면 `gallery.html`, 아니면 `sheet.png` 이미지를 대화에 띄운다). 동작에서 어색한 곳(잘림·놀란 눈·팔)은 여기서 고친다.
- **②에서 사용자가 "좋다"고 하기 전엔 4단계(zip 넘기기)로 가지 않는다.** idle 승인만으로 zip 을 주지 않는다.
- 눈·입처럼 안이 갈리면 두 안을 다른 폴더로 그려(`python3 make.py outA`, 값 바꿔 `outB`) `gallery.py outA outB` 한 페이지로 고르게 한다.

## 4. 넘기기

사용자가 11개 동작 전체를 승인했고 `validate.py` 가 `all ok` 면 zip 들을 준다(대화 환경이면 내려받기 링크로). zip 하나가 만들기 창 항목 하나다.

- `<이름>.zip`: 트레이 "캐릭터 > 만들기…" → 캐릭터 탭 → "+ 새로 만들기" → 이름 → "한꺼번에 넣기(.zip)…"(또는 창에 zip 끌어다 놓기) → 칸 확인 → 저장
- `<이름> 응가.zip`(만들었으면): 아이템 탭에서 같은 방법, 종류 **응가**
- 던질 것·먹이 zip: 아이템 탭, 종류 **던질 것/먹이**, '날아갈 때 돌리기'는 1단계에서 정한 대로

zip 안 파일 이름이 곧 칸 이름이다(`idle.png`…`offline.png`, 아이템은 `fly.png`·`impact.png`·`sound.wav`). 앱 밖에서 직접 만든 PNG 도 이 이름이면 그대로 들어간다. 친구 화면엔 친구가 "새 캐릭터·아이템 받기"를 누르거나 캐릭터 바꾸기 창을 열 때 들어간다.

## 완료 기준

- `validate.py` 가 `all ok`, `주의` 줄은 의도한 것인지 확인했다.
- 미리보기를 직접 봤고 사용자가 모양을 확인했다.
- 사용자에게: 무엇을 그렸는지, zip 이 어디 있는지, 앱에서 넣는 방법(위 4).
