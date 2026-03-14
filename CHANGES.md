# ForDecision Vercel 배포 오류 수정 내역

---

## v3 수정 (2026-03-15) — 현재 버전

> **오류 메시지:** `Build Failed — Function Runtimes must have a valid version, for example 'now-php@1.0.0'`

### 문제 원인

`vercel.json`에서 `builds` 방식 + `@vercel/python` 조합을 사용하면서 런타임 버전이 명시되지 않아 발생한 오류입니다.

```json
// ❌ 오류 발생 (v2 — builds 방식)
{
  "builds": [
    { "src": "api/analyze.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/api/analyze", "dest": "api/analyze.py" }
  ]
}
```

`builds` 방식은 레거시(구버전) 방식으로, Vercel CLI 50.x 이상에서는 `functions` 방식을 사용해야 합니다. `builds`를 사용할 경우 런타임 버전을 `@vercel/python@3.0.0`처럼 정확히 명시해야 하지만, 현재 Vercel에서 지원하는 Python 런타임 버전 형식과 맞지 않아 오류가 발생합니다.

### 수정 내용

```json
// ✅ 수정 후 (v3 — functions 방식)
{
  "functions": {
    "api/analyze.py": {
      "maxDuration": 60
    }
  }
}
```

`functions` 방식은 현재 Vercel 권장 방식으로, `runtime`을 별도로 명시하지 않아도 `api/` 폴더의 `.py` 파일을 자동으로 Python 런타임으로 인식합니다. Python 버전은 `.python-version` 파일 또는 `pyproject.toml`로 지정하거나, 미지정 시 Vercel이 최신 지원 버전(3.12)을 자동 선택합니다.

---

## v2 수정 (2026-03-11) — 이전 버전

> **오류 메시지:** `Build Failed — Invalid vercel.json file provided`

### 수정 내용

- `requirements.txt`: `PymuPDF` → `pymupdf>=1.23.0` (대소문자 오타 수정)
- `api/analyze.py`: `main.py` 로직을 Vercel Serverless Function 형식으로 래핑
- `vercel.json`: 신규 생성 (당시 `builds` 방식 적용)
- `.gitignore`: 신규 생성 (API 키 보호)

---

## 최종 프로젝트 구조

```
fordecision/
├── index.html           ← 랜딩페이지 (Day 3, 변경 없음)
├── style.css            ← 스타일시트 (Day 3, 변경 없음)
├── main.py              ← 로컬 CLI 테스트용 (변경 없음)
├── vercel.json          ★ 수정: builds → functions 방식으로 교체
├── api/
│   └── analyze.py       ← Vercel Serverless Function (변경 없음)
├── requirements.txt     ← pymupdf 소문자 + 버전 명시 (변경 없음)
├── .gitignore           ← API 키 보호 (변경 없음)
└── CHANGES.md           ← 이 문서
```

---

## 배포 전 최종 체크리스트

| 항목 | 상태 | 비고 |
|---|---|---|
| vercel.json — `functions` 방식 사용 | ✅ | `builds` 방식 제거 완료 |
| vercel.json — `maxDuration: 60` 설정 | ✅ | AI API 타임아웃 방지 |
| api/analyze.py — 소문자 `handler` 클래스 | ✅ | Vercel 필수 규칙 |
| api/analyze.py — CORS 헤더 포함 | ✅ | `Access-Control-Allow-Origin: *` |
| requirements.txt — `pymupdf` 소문자 | ✅ | 빌드 실패 방지 |
| .gitignore — `.env.local` 포함 | ✅ | API 키 노출 방지 |
| Vercel 환경변수 `OPENAI_API_KEY` 등록 | ⬜ | Vercel 대시보드에서 수동 설정 필요 |
| Vercel Fluid Compute 활성화 | ⬜ | Settings → Functions → Enable |

---

## 재배포 방법

```bash
cd ~/fordecision

git add vercel.json CHANGES.md
git commit -m 'Fix: vercel.json builds → functions 방식 교체 (런타임 버전 오류 수정)'
git push

# Vercel 대시보드 → Deployments → Ready (녹색) 확인
```
