#!/usr/bin/env python
# coding: utf-8

import os
import sys
import json
import fitz  # PyMuPDF
from anthropic import Anthropic

# Anthropic API 키 설정
# 중요: 실제 환경에서는 환경 변수에서 키를 로드해야 합니다.
# 예: export ANTHROPIC_API_KEY='your-api-key'
client = Anthropic(api_key=os.getenv("ThMiVtZi5U_8fDvWi9pJ9lpl5BDSTZN7KSarGWhGOrwWH6y7XoqhImYRMoBo1RHUOaTzo4ku8sdGxyNFAdXyJQ"))

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
    """추출된 텍스트를 Anthropic (Claude) API를 통해 분석하고 JSON으로 반환합니다."""
    system_prompt = "You are an expert in analyzing pitch decks and extracting key information into a structured JSON format. Please output only the JSON object."
    
    prompt = f"""다음은 피치덱의 전체 텍스트입니다. 이 내용을 분석하여 아래 JSON 형식에 맞춰 핵심 정보를 추출해 주세요. 반드시 JSON 객체만 출력해야 합니다.

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
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2048,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            # Claude API 응답에서 텍스트 콘텐츠 추출
            result_text = response.content[0].text
            # JSON 객체만 정확히 파싱하기 위한 처리
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                result_json = result_text[json_start:json_end]
                return json.loads(result_json)
            else:
                raise json.JSONDecodeError("No JSON object found in response", result_text, 0)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to decode JSON from Claude response. Retrying... Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while calling Claude API: {e}")
            return {}

    print("Error: Failed to get a valid JSON response from Claude after multiple attempts.")
    return {}

def main():
    """메인 실행 함수"""
    if len(sys.argv) < 2:
        print("Usage: python main_claude.py <path_to_pdf>")
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

    print("2. Analyzing text with Anthropic (Claude) API...")
    analysis_result = analyze_pitch_deck(pitch_deck_text)

    if not analysis_result:
        print("Failed to get analysis. Exiting.")
        sys.exit(1)

    output_path = "report_claude.json"
    print(f"3. Saving analysis to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Analysis complete. {output_path} has been created.")

if __name__ == "__main__":
    main()
