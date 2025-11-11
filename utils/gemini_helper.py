"""
Google Gemini API 연동 헬퍼
"""
import google.generativeai as genai
from typing import Dict, List, Optional
import time

class GeminiHelper:
    def __init__(self, api_key: str):
        """Gemini API 초기화"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_response(
        self,
        system_prompt: str,
        user_context: Dict,
        retry_count: int = 3
    ) -> str:
        """
        Gemini API를 사용하여 응답 생성

        Args:
            system_prompt: 시스템 프롬프트
            user_context: 사용자 컨텍스트 (phase, 수집된 데이터, 마지막 답변 등)
            retry_count: 재시도 횟수

        Returns:
            생성된 응답 텍스트
        """
        # 컨텍스트를 프롬프트에 통합
        full_prompt = self._build_full_prompt(system_prompt, user_context)

        for attempt in range(retry_count):
            try:
                response = self.model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    return self._get_fallback_response(user_context)

    def _build_full_prompt(self, system_prompt: str, context: Dict) -> str:
        """시스템 프롬프트와 컨텍스트를 결합"""
        prompt_parts = [system_prompt, "\n\n**현재 상황:**"]

        # Phase 정보
        if "current_phase" in context:
            prompt_parts.append(f"- 현재 단계: Phase {context['current_phase']}")

        # 수집된 데이터
        if "collected_data" in context and context["collected_data"]:
            prompt_parts.append("\n**수집된 정보:**")
            for key, value in context["collected_data"].items():
                prompt_parts.append(f"- {key}: {value}")

        # 마지막 질문/답변
        if "last_question" in context:
            prompt_parts.append(f"\n**직전 질문:** {context['last_question']}")
        if "last_answer" in context:
            prompt_parts.append(f"**고객 답변:** {context['last_answer']}")

        # 요청 사항
        if "request" in context:
            prompt_parts.append(f"\n**요청사항:**\n{context['request']}")

        return "\n".join(prompt_parts)

    def _get_fallback_response(self, context: Dict) -> str:
        """API 실패 시 대체 응답"""
        phase = context.get("current_phase", 1)

        fallback_responses = {
            1: "네, 잘 알겠습니다. 다음 질문으로 넘어가겠습니다.",
            2: "좋은 경험이셨군요. 조금 더 여쭤보겠습니다.",
            3: "명확하게 말씀해 주셔서 감사합니다. 계속 진행하겠습니다.",
            4: "고객님의 니즈를 잘 이해했습니다.",
            5: "마지막 단계입니다. 조금만 더 진행하겠습니다."
        }

        return fallback_responses.get(phase, "네, 알겠습니다.")

    def generate_empathy_comment(
        self,
        question: str,
        answer: str,
        context: Dict
    ) -> str:
        """
        답변에 대한 공감 멘트 생성

        Args:
            question: 질문 내용
            answer: 사용자 답변
            context: 전체 컨텍스트

        Returns:
            공감 멘트
        """
        request = f"""
고객이 다음 질문에 이렇게 답변했습니다:

**질문:** {question}
**답변:** {answer}

이 답변에 대해 공감하고 긍정적으로 반응하는 멘트를 1~2문장으로 작성해주세요.
그리고 자연스럽게 다음 질문으로 연결하는 전환 문구를 추가해주세요.

**조건:**
- 존댓말 사용
- 따뜻하면서도 전문적인 톤
- 고객의 선택을 인정하고 격려
- 필요시 전문가적 인사이트 추가
"""

        context["request"] = request
        return self.generate_response("", context)

    def generate_question_options(
        self,
        question_type: str,
        context: Dict
    ) -> List[str]:
        """
        맥락 기반 동적 선택지 생성

        Args:
            question_type: 질문 유형 (예: "marketing_channels", "budget_allocation")
            context: 수집된 데이터

        Returns:
            선택지 리스트
        """
        request = f"""
다음 질문 유형에 맞는 객관식 선택지를 생성해주세요: {question_type}

**조건:**
- 4~6개의 선택지
- 명확하고 상호배타적
- 마지막은 항상 "기타"
- 고객의 업종과 상황에 맞게 맞춤화
- JSON 배열 형식으로 반환: ["선택지1", "선택지2", ...]

선택지만 반환해주세요 (설명 없이).
"""

        context["request"] = request
        response = self.generate_response("", context)

        # 간단한 파싱 (실제로는 더 robust하게 구현 필요)
        try:
            import json
            return json.loads(response)
        except:
            # 파싱 실패 시 기본 선택지
            return ["옵션 1", "옵션 2", "옵션 3", "기타"]

    def generate_proposal(
        self,
        collected_data: Dict,
        proposal_template: str
    ) -> str:
        """
        수집된 데이터 기반 제안서 생성

        Args:
            collected_data: 30개 질문을 통해 수집된 모든 데이터
            proposal_template: 제안서 템플릿

        Returns:
            완성된 제안서 (마크다운)
        """
        # 데이터 정리
        data_summary = self._format_collected_data(collected_data)

        request = f"""
다음 고객 정보를 바탕으로 전문적인 마케팅 전략 제안서를 작성해주세요.

**수집된 고객 정보:**
{data_summary}

**제안서 템플릿:**
{proposal_template}

**작성 지침:**
1. 모든 섹션을 빠짐없이 작성
2. 구체적인 숫자와 예산안 포함
3. 실행 가능한 액션 아이템 제시
4. 고객의 제약사항과 우려사항 반영
5. 전문적이면서도 이해하기 쉽게 작성

제안서를 마크다운 형식으로 작성해주세요.
"""

        context = {
            "collected_data": collected_data,
            "request": request
        }

        return self.generate_response("", context)

    def _format_collected_data(self, data: Dict) -> str:
        """수집된 데이터를 읽기 쉬운 형식으로 변환"""
        lines = []
        for phase, phase_data in data.items():
            lines.append(f"\n**{phase}:**")
            for key, value in phase_data.items():
                lines.append(f"  - {key}: {value}")
        return "\n".join(lines)
