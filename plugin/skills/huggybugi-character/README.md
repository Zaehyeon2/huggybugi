# huggybugi-character

허기부기(Huggybugi) 데스크톱 펫 앱에 올릴 48px 픽셀 캐릭터를 AI 가 **코드로** 그리게 하는 스킬이에요. 사진이나 그림을 주고 "캐릭터 만들어줘" 하면 동작 11개를 그려(원하면 그 캐릭터 응가·던질 것·먹이도) PNG 와 zip 으로 줘요. zip 은 앱 만들기 창 "한꺼번에 넣기(.zip)"로 한 번에 들어가요.

특정 AI 에 묶이지 않아요. 코드를 실행할 수 있는 AI(Claude Code, ChatGPT, Codex, Gemini CLI 등)면 돼요.

## 필요한 것

- AI 가 Python 코드를 **실행**할 수 있어야 해요. 실행을 못 하면 코드만 써 주고 그림 파일은 못 만들어요.
- 내 컴퓨터에서 돌릴 땐 Python 3.10 이상과 Pillow: `python3 -m pip install pillow`

## AI 별 쓰는 법

어느 AI 든 가장 확실한 방법은 같아요. **이 폴더를 zip 으로(또는 폴더째) 주고 "SKILL.md 대로 이 사진으로 허기부기 캐릭터 만들어줘"** 라고 하는 거예요. 아래는 스킬로 넣어 두고 매번 알아서 쓰게 하는 방법이에요. 메뉴 이름은 서비스가 바꾸기도 해요.

**Claude (claude.ai 웹·앱)**: 설정의 Capabilities(또는 Customize > Skills)에서 "Upload skill" 로 이 폴더 zip 을 올려요. 코드 실행이 켜진 유료 요금제에서 돼요.

**ChatGPT**: Skills 를 쓸 수 있는 요금제면 Skills 에서 이 폴더 zip 을 올려요. 아니면 대화에 zip 과 사진을 같이 올리고 위 문장으로 부탁해요. 코드 실행이 되는 모델이어야 해요.

**Gemini (웹·앱)**: Skills 에서 이 폴더 zip 을 올려요(개인 계정). Gemini 가 코드를 실행하지 못하면 그림 파일 대신 코드만 줄 수 있어요. 그땐 받은 코드를 아래 "직접 돌려 보기"처럼 내 컴퓨터에서 돌려요.

**Claude Code**: 플러그인으로 설치해요. `/plugin marketplace add Zaehyeon2/huggybugi` 다음 `/plugin install huggybugi@huggybugi`.

```bash
cp -r huggybugi-character ~/.claude/skills/
```

**Gemini CLI**: 폴더를 `~/.gemini/skills/` 에 복사해요.

**Codex**: `codex plugin marketplace add Zaehyeon2/huggybugi` 다음 `codex plugin add huggybugi@huggybugi`. 다른 터미널 AI 는 이 폴더를 작업 폴더에 두고 `AGENTS.md` 에 "허기부기 캐릭터 요청은 huggybugi-character/SKILL.md 를 따른다" 한 줄을 넣어요.

다 되면 zip 과 미리보기를 보여 줘요. 고칠 점은 말로 하면 돼요("눈 더 크게", "다리 짧게").

## 앱에 넣기

1. 트레이 메뉴 "캐릭터 > 만들기…" → 캐릭터 탭 → "+ 새로 만들기", 이름 쓰기
2. "한꺼번에 넣기(.zip)…"로 `<이름>.zip` 을 고르거나 창에 끌어다 놓기 → 칸 확인 → 저장
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
