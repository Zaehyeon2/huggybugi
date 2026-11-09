# huggybugi-character

허기부기(Huggybugi) 데스크톱 펫 앱에 올릴 48px 픽셀 캐릭터를 AI 가 **코드로** 그리게 하는 스킬이에요. 사진이나 그림을 주고 "캐릭터 만들어줘" 하면 동작 11개를 그려(원하면 그 캐릭터 응가·던질 것·먹이도) PNG 와 zip 으로 줘요. zip 은 앱 만들기 창 "한꺼번에 넣기 > zip 파일…"로 한 번에 들어가요.

Claude Code·Codex 처럼 코드를 실행하는 AI 용이에요. ChatGPT·Gemini 웹·앱을 쓴다면 소개 사이트의 "이미지 AI로 만들기"가 더 쉬워요.

## 필요한 것

- 내 컴퓨터에서 돌릴 땐 Python 3.10 이상과 Pillow: `python3 -m pip install pillow`

## 설치

**Claude Code**

```bash
claude plugin marketplace add Zaehyeon2/huggybugi
claude plugin install huggybugi@huggybugi
```

**Codex**

```bash
codex plugin marketplace add Zaehyeon2/huggybugi
codex plugin add huggybugi@huggybugi
```

설치하면 사진과 함께 "허기부기 캐릭터 만들어줘" 라고 해요.

다 되면 zip 과 미리보기를 보여 줘요. 고칠 점은 말로 하면 돼요("눈 더 크게", "다리 짧게").

## 앱에 넣기

1. 트레이 메뉴 "캐릭터 > 만들기…" → 캐릭터 탭 → "+ 새로 만들기", 이름 쓰기
2. "한꺼번에 넣기 > zip 파일…"로 `<이름>.zip` 을 고르거나 창에 끌어다 놓기 → 칸 확인 → 저장
3. 응가를 만들었으면 아이템 탭에서 같은 방법으로 `<이름> 응가.zip`, 종류는 **응가**. 던질 것·먹이도 아이템 탭에서 종류를 골라요.

## 직접 돌려 보기

이 폴더 안에서:

```bash
python3 examples/ddeogi/make.py out     # 예시 캐릭터 떠기 → out/
python3 scripts/validate.py out         # 앱 규칙 검사, all ok
python3 scripts/gallery.py out          # out/gallery.html 을 브라우저로
```

새 캐릭터는 `scripts/template.py` 를 다른 곳에 `make.py` 로 복사해 고치고, 그림 도구 위치를 `HB_LIB` 로 알려 줘요.

```bash
HB_LIB=/스킬/폴더/scripts python3 make.py out
```

규격과 그리기 요령은 `references/drawing.md`.
