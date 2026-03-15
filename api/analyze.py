import json
import os
import fitz  # PyMuPDF
from openai import OpenAI
from http.server import BaseHTTPRequestHandler

# 환경변수에서 API 키 로드 (절대 코드에 직접 입력 금지)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_pitch_deck(text: str) -> dict:
    """추출된 텍스트를 OpenAI API를 통해 분석하고 JSON으로 반환합니다."""
    prompt = f"""다음은 피치덱의 전체 텍스트입니다. 이 내용을 분석하여 아래 JSON 형식에 맞춰 핵심 정보를 추출해 주세요.

--- 텍스트 시작 ---
{text}
--- 텍스트 끝 ---

JSON 형식:
{{
  "company_name": "회사명",
  "product_service": "제품/서비스 요약",
  "problem": "해결하려는 문제",
  "solution": "제시하는 해결책",
  "market_size": "목표 시장 규모 및 잠재력",
  "team": "핵심 팀원 및 역량",
  "financials": {{
    "revenue": "매출 현황 또는 전망",
    "funding_ask": "투자 유치 희망 금액"
  }}
}}
"""
    for _ in range(2):  # 최대 2번 재시도
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in analyzing pitch decks and extracting key information into a structured JSON format."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            result_json = response.choices[0].message.content
            return json.loads(result_json)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to decode JSON from OpenAI response. Retrying... Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while calling OpenAI API: {e}")
            return {}
    return {}


class handler(BaseHTTPRequestHandler):
    """
    Vercel Python Serverless Function 필수 구조.
    클래스명은 반드시 소문자 handler 여야 합니다.
    """

    def do_OPTIONS(self):
        """OPTIONS — CORS preflight 처리"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        """POST /api/analyze — PDF 텍스트 분석 요청 처리"""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length))
            pdf_text = body.get("text", "")

            if not pdf_text:
                self._json({"error": "text 필드가 비어 있습니다"}, 400)
                return

            result = analyze_pitch_deck(pdf_text)
            self._json(result, 200)
        except json.JSONDecodeError:
            self._json({"error": "JSON 파싱 오류"}, 400)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def do_GET(self):
        """GET /api/analyze — 헬스체크용"""
        self._json({"status": "ok", "service": "fordecision-api"}, 200)

    def _json(self, data: dict, status: int):
        """JSON 응답 헬퍼 — CORS 헤더 포함"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
