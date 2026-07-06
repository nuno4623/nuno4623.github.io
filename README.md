# 수업자료 사이트 (nuno4623.github.io)

워크시트를 올리면 **QR 코드 · 안내페이지가 자동 생성되고 GitHub Pages 로 자동 배포**됩니다.
주소: `https://nuno4623.github.io/`

## 🚀 새 워크시트 배포하는 법

1. `lessons/<학년>/<주제>/` 폴더에 워크시트 **HTML 파일**을 넣는다
   (GitHub 웹에서 *Add file ▸ Upload files* 로 드래그해도 됨)
2. 커밋/푸시한다
3. 끝. 1~2분 뒤 자동으로:
   - 각 HTML → **QR 코드**(`qr/<이름>.svg`) 생성
   - 그 폴더 **QR 모음 안내페이지**(`index.html`) 생성/갱신
   - **루트 목록페이지** 갱신
   - **Pages 배포**

> 파일명이 곧 주소가 됩니다. 예) `lessons/음악5/음악문화탐구/samguk.html`
> → `https://nuno4623.github.io/lessons/음악5/음악문화탐구/samguk.html`

## 🧩 두 가지 워크시트 유형 (템플릿 제공)

| 유형 | 위치 | 설명 |
|---|---|---|
| **단독 HTML형** | `templates/standalone/worksheet.html` | 입력 → 🖼 이미지로 저장(PNG 제출) |
| **앱스스크립트 제출형** | `templates/appsscript/` | 제출 → Google Sheets 자동 기록 (`README.md` 참고) |

템플릿을 복사해 `[바꾸기]` 표시된 곳(제목·색·문항)만 고치면 됩니다.

## 🎛 폴더별 옵션 — `_meta.json` (선택)

폴더에 `_meta.json` 을 두면 안내페이지의 제목/배지/순서/설명/색을 지정할 수 있습니다.
없으면 HTML 에서 자동 추출합니다(제목·대표색).

```json
{
  "badge": "5학년 음악 · 음악문화 탐구",
  "title": "시대별 음악문화 조사",
  "lead": "모둠별로 QR 을 스캔해 워크시트를 열고 내용을 채우세요.",
  "items": [
    { "file": "samguk.html", "name": "삼국시대", "sub": "고구려·백제·신라", "color": "#E53935" }
  ]
}
```

## 🔧 로컬에서 미리 만들어 보기(선택)

```bash
pip install qrcode
python tools/build_site.py     # qr/ · index.html 들을 로컬에서 생성
```

## ⚙️ 최초 1회 설정 (저장소 생성 직후)

- **Settings ▸ Pages ▸ Build and deployment ▸ Source = GitHub Actions** 로 지정
- 이후에는 push 만 하면 자동 배포됩니다.
