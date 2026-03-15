import os
import sys
import json
import fitz  # PyMuPDF
from openai import OpenAI

# OpenAI API 키 설정
# 중요: 실제 환경에서는 환경 변수에서 키를 로드해야 합니다.
# 예: export OPENAI_API_KEY='your-api-key'
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_path: str) -> str:
    """PDF 파일에서 모든 텍스트를 추출합니다."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

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
                    {"role": "system", "content": "You are an expert in analyzing pitch decks and extracting key information into a structured JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            # OpenAI 라이브러리 v1.x.x 에서는 .choices[0].message.content 로 접근
            result_json = response.choices[0].message.content
            return json.loads(result_json)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to decode JSON from OpenAI response. Retrying... Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while calling OpenAI API: {e}")
            return {}

    print("Error: Failed to get a valid JSON response from OpenAI after multiple attempts.")
    return {}

def main():
    """메인 실행 함수"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        sys.exit(1)

    print(f"1. Extracting text from {pdf_path}...")
    pitch_deck_text = extract_text_from_pdf(pdf_path)

    if not pitch_deck_text:
        print("Could not extract text. Exiting.")
        sys.exit(1)

    print("2. Analyzing text with OpenAI API...")
    analysis_result = analyze_pitch_deck(pitch_deck_text)

    if not analysis_result:
        print("Failed to get analysis. Exiting.")
        sys.exit(1)

    output_path = "report.json"
    print(f"3. Saving analysis to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)

    print("\n✅ Analysis complete. report.json has been created.")

if __name__ == "__main__":
    main()
