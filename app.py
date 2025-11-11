"""
AI 마케팅 컨설턴트 - 민준
Streamlit 기반 객관식 대화형 마케팅 전략 컨설팅 서비스
"""
import streamlit as st
from datetime import datetime
from utils.gemini_helper import GeminiHelper
from utils.session_manager import SessionManager
from config.persona import (
    PERSONA_NAME, PERSONA_EXPERIENCE, SYSTEM_PROMPT,
    PHASE_GOALS, PROPOSAL_PROMPT
)

# 페이지 설정
st.set_page_config(
    page_title=f"AI 마케팅 컨설턴트 - {PERSONA_NAME}",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1976D2;
        margin-bottom: 1rem;
    }
    .assistant-message {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: right;
    }
    .phase-badge {
        background-color: #4CAF50;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
    }
    .summary-box {
        background-color: #FFF9C4;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_app():
    """앱 초기화"""
    SessionManager.initialize()

    # Gemini API 키 확인
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        if api_key == "your-api-key-here":
            st.error("⚠️ Gemini API 키를 설정해주세요! (.streamlit/secrets.toml)")
            st.stop()
        if "gemini" not in st.session_state:
            st.session_state.gemini = GeminiHelper(api_key)
    except Exception as e:
        st.error(f"⚠️ API 키 로드 실패: {e}")
        st.info("`.streamlit/secrets.toml` 파일에 `GEMINI_API_KEY`를 설정해주세요.")
        st.stop()

def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        st.markdown(f"### 🎨 {PERSONA_NAME}의 마케팅 컨설팅")
        st.markdown(f"*{PERSONA_EXPERIENCE} 경력 광고 전문가*")

        st.markdown("---")

        # 진행 상황
        st.markdown("### 📊 진행 상황")
        progress = SessionManager.get_progress_percentage()
        st.progress(progress / 100)
        st.markdown(f"**{progress:.0f}% 완료**")

        current_phase = st.session_state.current_phase
        if current_phase <= 5:
            phase_info = PHASE_GOALS[current_phase]
            st.markdown(f"**현재 단계:** Phase {current_phase}")
            st.markdown(f"*{phase_info['name']}*")

        st.markdown("---")

        # 수집된 정보 요약
        st.markdown("### 📝 수집 정보")
        summary = SessionManager.get_summary()
        if summary:
            for key, value in summary.items():
                st.markdown(f"**{key}:** {value}")
        else:
            st.markdown("*아직 수집된 정보가 없습니다*")

        st.markdown("---")

        # 새 대화 시작
        if st.button("🔄 새 대화 시작", use_container_width=True):
            SessionManager.reset_conversation()
            st.rerun()

def render_chat_history():
    """대화 히스토리 렌더링"""
    for msg in st.session_state.conversation_history:
        if msg["role"] == "assistant":
            st.markdown(
                f'<div class="assistant-message">🧑 <strong>{PERSONA_NAME}:</strong><br>{msg["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="user-message">👤 <strong>나:</strong><br>{msg["content"]}</div>',
                unsafe_allow_html=True
            )

def ask_question(question_data: dict):
    """질문하고 답변 받기"""
    question_text = question_data["question"]
    question_type = question_data["type"]
    options = question_data["options"]
    question_key = question_data["key"]

    # 질문 표시
    st.markdown(f"### {question_text}")

    # 답변 위젯
    answer = None
    answer_key = f"answer_{question_key}"

    if question_type == "single_choice":
        answer = st.radio(
            "선택해주세요:",
            options,
            key=answer_key,
            label_visibility="collapsed"
        )

    elif question_type == "multiple_choice":
        answer = st.multiselect(
            "선택해주세요 (복수 선택 가능):",
            options,
            key=answer_key
        )

    elif question_type == "scale":
        answer = st.slider(
            "척도를 선택해주세요:",
            min_value=options["min"],
            max_value=options["max"],
            value=options.get("default", 5),
            key=answer_key
        )

    # 답변 제출 버튼
    if st.button("✅ 선택 완료", key=f"submit_{question_key}", type="primary"):
        if answer:
            # 답변 저장
            SessionManager.add_message("user", str(answer))
            SessionManager.save_answer(
                st.session_state.current_phase,
                question_key,
                answer
            )

            # 요약 정보 업데이트
            if "summary_key" in question_data:
                SessionManager.update_summary(
                    question_data["summary_key"],
                    str(answer)
                )

            # AI 공감 멘트 생성
            context = SessionManager.get_context_for_ai()
            empathy = st.session_state.gemini.generate_empathy_comment(
                question_text,
                str(answer),
                context
            )
            SessionManager.add_message("assistant", empathy)

            # 다음 질문으로 이동
            st.session_state.current_question += 1

            st.rerun()
        else:
            st.warning("답변을 선택해주세요!")

def get_question_for_phase(phase: int, question_num: int) -> dict:
    """Phase와 질문 번호에 따라 질문 반환"""
    # Phase 1: 라포 형성 및 비즈니스 이해
    phase_1_questions = [
        {
            "key": "visit_reason",
            "question": "어떤 계기로 찾아주셨나요?",
            "type": "single_choice",
            "options": [
                "신규 사업을 시작하려고 합니다",
                "기존 브랜드를 리뉴얼하려고 합니다",
                "매출이 감소해서 돌파구가 필요합니다",
                "경쟁사 대응 전략이 필요합니다",
                "기타"
            ],
            "summary_key": "방문계기"
        },
        {
            "key": "industry",
            "question": "어떤 업종에서 사업을 하시나요?",
            "type": "single_choice",
            "options": [
                "화장품/뷰티",
                "식음료/F&B",
                "패션/의류",
                "IT/테크",
                "교육/학원",
                "헬스케어/의료",
                "부동산/인테리어",
                "기타"
            ],
            "summary_key": "업종"
        },
        {
            "key": "target_age",
            "question": "주요 타겟 연령층은 어떻게 되나요?",
            "type": "multiple_choice",
            "options": ["10대", "20대", "30대", "40대", "50대 이상", "전 연령층"]
        },
        {
            "key": "target_gender",
            "question": "타겟 성별은 어떻게 되나요?",
            "type": "single_choice",
            "options": ["여성 중심", "남성 중심", "성별 무관"]
        },
        {
            "key": "product_stage",
            "question": "현재 제품/서비스는 어느 단계에 있나요?",
            "type": "single_choice",
            "options": [
                "아이디어 단계 (기획 중)",
                "개발 중 (출시 전)",
                "샘플/테스트 완료",
                "출시 준비 완료",
                "이미 출시했지만 마케팅 부족"
            ]
        }
    ]

    # Phase 2: 기존 마케팅 경험
    phase_2_questions = [
        {
            "key": "marketing_experience",
            "question": "이전에 마케팅을 해보신 적이 있으신가요?",
            "type": "single_choice",
            "options": [
                "전혀 없습니다 (이번이 처음)",
                "약간 있습니다 (SNS 운영 정도)",
                "어느 정도 있습니다 (광고 집행 경험)",
                "많이 있습니다 (다른 사업 경험)"
            ]
        },
        {
            "key": "used_channels",
            "question": "그동안 사용해본 마케팅 채널은 무엇인가요?",
            "type": "multiple_choice",
            "options": [
                "인스타그램",
                "페이스북",
                "유튜브",
                "틱톡/릴스",
                "네이버 블로그",
                "네이버 검색광고",
                "구글 광고",
                "오프라인 전단/배너",
                "사용 안 함"
            ]
        },
        {
            "key": "satisfaction",
            "question": "기존 마케팅 활동에 대한 만족도는 어떠셨나요?",
            "type": "scale",
            "options": {"min": 1, "max": 10, "default": 5}
        },
        {
            "key": "previous_budget",
            "question": "이전에 마케팅에 투입한 예산 규모는 어느 정도였나요?",
            "type": "single_choice",
            "options": [
                "거의 없음 (무료 운영)",
                "100만원 미만",
                "100~500만원",
                "500~1000만원",
                "1000만원 이상"
            ]
        },
        {
            "key": "pain_points",
            "question": "마케팅하시면서 가장 어려웠던 점은 무엇이었나요?",
            "type": "multiple_choice",
            "options": [
                "무엇부터 해야 할지 몰랐다",
                "예산이 부족했다",
                "효과 측정이 어려웠다",
                "콘텐츠 제작이 어려웠다",
                "시간이 부족했다",
                "전문성이 부족했다"
            ]
        }
    ]

    # Phase 3: 목표 및 제약사항
    phase_3_questions = [
        {
            "key": "campaign_goals",
            "question": "이번 마케팅의 가장 중요한 목표는 무엇인가요? (최대 2개)",
            "type": "multiple_choice",
            "options": [
                "브랜드 인지도 향상",
                "온라인 판매 증대",
                "오프라인 매장 방문",
                "SNS 팔로워 증가",
                "신규 고객 확보",
                "기존 고객 재구매"
            ],
            "summary_key": "목표"
        },
        {
            "key": "budget",
            "question": "투입 가능한 마케팅 예산은 어느 정도이신가요?",
            "type": "single_choice",
            "options": [
                "1000만원 미만",
                "1000만원 ~ 3000만원",
                "3000만원 ~ 5000만원",
                "5000만원 ~ 1억",
                "1억 ~ 3억",
                "3억 이상",
                "아직 미정"
            ],
            "summary_key": "예산"
        },
        {
            "key": "budget_flexibility",
            "question": "예산이 상황에 따라 조정 가능하신가요?",
            "type": "single_choice",
            "options": [
                "고정 (절대 변경 불가)",
                "약간 유연 (±10%)",
                "유연 (±30%)",
                "매우 유연 (성과에 따라 증액 가능)"
            ]
        },
        {
            "key": "duration",
            "question": "캠페인은 얼마 동안 진행하고 싶으신가요?",
            "type": "single_choice",
            "options": [
                "1개월 (단기 집중)",
                "3개월 (분기)",
                "6개월 (반기)",
                "1년 (연간)",
                "지속적으로"
            ],
            "summary_key": "기간"
        },
        {
            "key": "start_time",
            "question": "언제부터 시작하고 싶으신가요?",
            "type": "single_choice",
            "options": [
                "즉시 (2주 이내)",
                "1개월 이내",
                "2~3개월 후",
                "특정 시즌",
                "아직 미정"
            ]
        },
        {
            "key": "constraints",
            "question": "마케팅 진행 시 피하거나 고려해야 할 사항이 있나요?",
            "type": "multiple_choice",
            "options": [
                "과장 광고 우려",
                "특정 플랫폼 제외",
                "오프라인 불가",
                "예산 엄수 (초과 불가)",
                "없음"
            ]
        }
    ]

    # Phase 4: 타겟 인사이트
    phase_4_questions = [
        {
            "key": "customer_interests",
            "question": "타겟 고객이 가장 관심 있어 할 주제는 무엇일까요?",
            "type": "multiple_choice",
            "options": [
                "가격/가성비",
                "품질/성능",
                "트렌드/최신 유행",
                "환경/지속가능성",
                "건강/웰빙",
                "편리함/시간 절약"
            ]
        },
        {
            "key": "media_platforms",
            "question": "타겟 고객이 가장 많이 사용하는 플랫폼은 어디일까요?",
            "type": "multiple_choice",
            "options": [
                "인스타그램",
                "유튜브",
                "틱톡",
                "네이버 (블로그/카페)",
                "카카오톡 채널",
                "페이스북"
            ]
        },
        {
            "key": "purchase_decision",
            "question": "고객이 구매 결정할 때 가장 중요하게 보는 요소는?",
            "type": "multiple_choice",
            "options": [
                "가격",
                "리뷰/후기",
                "브랜드 신뢰도",
                "제품 사양/성능",
                "디자인",
                "인플루언서 추천"
            ]
        },
        {
            "key": "purchase_channel",
            "question": "고객이 주로 어디서 구매하나요?",
            "type": "multiple_choice",
            "options": [
                "네이버 스마트스토어",
                "쿠팡",
                "자사몰",
                "오프라인 매장",
                "기타 온라인몰"
            ]
        },
        {
            "key": "differentiators",
            "question": "경쟁사 대비 우리의 가장 큰 강점은 무엇인가요?",
            "type": "multiple_choice",
            "options": [
                "가격 경쟁력",
                "품질/성능",
                "고객 서비스",
                "브랜드 스토리",
                "독특한 디자인",
                "아직 모르겠다"
            ]
        }
    ]

    # Phase 5: 전략 선호
    phase_5_questions = [
        {
            "key": "approach",
            "question": "어떤 스타일의 마케팅을 원하시나요?",
            "type": "single_choice",
            "options": [
                "공격적/빠른 성장 (리스크 감수)",
                "안정적/장기적 성장",
                "바이럴/화제성 중심",
                "데이터 기반/과학적",
                "스토리텔링/감성적"
            ]
        },
        {
            "key": "online_offline_ratio",
            "question": "온라인과 오프라인 예산 비중은 어떻게 하고 싶으신가요?",
            "type": "single_choice",
            "options": [
                "100% 온라인",
                "온라인 80% : 오프라인 20%",
                "온라인 60% : 오프라인 40%",
                "반반 (50:50)",
                "오프라인 중심"
            ]
        },
        {
            "key": "influencer_importance",
            "question": "인플루언서/크리에이터 협업에 대해 어떻게 생각하시나요?",
            "type": "single_choice",
            "options": [
                "매우 중요 (예산 많이 투입)",
                "중요 (적절히 활용)",
                "보조 수단 (소규모)",
                "불필요",
                "잘 모르겠다"
            ]
        },
        {
            "key": "main_concern",
            "question": "마지막으로, 마케팅 진행하면서 가장 걱정되는 점은 무엇인가요?",
            "type": "single_choice",
            "options": [
                "예산 대비 효과가 없을까봐",
                "브랜드 이미지가 잘못 전달될까봐",
                "경쟁사에 밀릴까봐",
                "시간이 너무 오래 걸릴까봐",
                "특별히 없다"
            ]
        }
    ]

    phase_questions = {
        1: phase_1_questions,
        2: phase_2_questions,
        3: phase_3_questions,
        4: phase_4_questions,
        5: phase_5_questions
    }

    questions = phase_questions.get(phase, [])
    if question_num < len(questions):
        return questions[question_num]
    else:
        return None

def main():
    """메인 함수"""
    initialize_app()

    # 헤더
    st.markdown(f'<div class="main-header">🎨 AI 마케팅 컨설턴트 - {PERSONA_NAME}</div>', unsafe_allow_html=True)
    st.markdown(f"*{PERSONA_EXPERIENCE} 경력 광고 전문가가 1:1 맞춤 전략을 제안합니다*")

    # 사이드바
    render_sidebar()

    # 시작 메시지
    if len(st.session_state.conversation_history) == 0:
        welcome_msg = f"""안녕하세요! 저는 {PERSONA_EXPERIENCE} 동안 광고대행사에서 다양한 브랜드와 함께 일해온 {PERSONA_NAME}입니다.

오늘은 고객님의 비즈니스를 깊이 이해하고, 맞춤형 마케팅 전략을 제안해드리고자 합니다.

몇 가지 질문을 드릴 테니, 편하게 선택해주시면 됩니다. 시작하시겠습니까?"""
        SessionManager.add_message("assistant", welcome_msg)

    # 대화 히스토리 표시
    render_chat_history()

    # 대화 완료 여부 확인
    if SessionManager.is_complete():
        st.markdown("---")
        st.success("✅ 모든 질문이 완료되었습니다!")

        if st.session_state.proposal is None:
            if st.button("📄 제안서 생성하기", type="primary"):
                with st.spinner("전문가 수준의 제안서를 생성하고 있습니다..."):
                    all_data = SessionManager.get_all_collected_data()
                    proposal = st.session_state.gemini.generate_proposal(
                        all_data,
                        PROPOSAL_PROMPT
                    )
                    st.session_state.proposal = proposal
                st.rerun()
        else:
            st.markdown("### 📄 마케팅 전략 제안서")
            st.markdown(st.session_state.proposal)

            # 다운로드 버튼
            st.download_button(
                label="📥 제안서 다운로드 (Markdown)",
                data=st.session_state.proposal,
                file_name=f"marketing_proposal_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
    else:
        # 현재 질문 가져오기
        current_question_data = get_question_for_phase(
            st.session_state.current_phase,
            st.session_state.current_question
        )

        if current_question_data:
            st.markdown("---")
            ask_question(current_question_data)
        else:
            # Phase 완료, 다음 Phase로 이동
            SessionManager.move_to_next_phase()
            if not SessionManager.is_complete():
                phase_info = PHASE_GOALS[st.session_state.current_phase]
                transition_msg = f"좋습니다! 이제 '{phase_info['name']}' 단계로 넘어가겠습니다."
                SessionManager.add_message("assistant", transition_msg)
            st.rerun()

if __name__ == "__main__":
    main()
