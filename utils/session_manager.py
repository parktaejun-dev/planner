"""
Streamlit Session State 관리 유틸리티
"""
import streamlit as st
from typing import Dict, List, Any
from datetime import datetime

class SessionManager:
    """Streamlit Session State를 관리하는 클래스"""

    @staticmethod
    def initialize():
        """Session State 초기화"""
        if "initialized" not in st.session_state:
            st.session_state.initialized = True
            st.session_state.current_phase = 1
            st.session_state.current_question = 0
            st.session_state.conversation_history = []
            st.session_state.collected_data = {
                "phase_1": {},
                "phase_2": {},
                "phase_3": {},
                "phase_4": {},
                "phase_5": {}
            }
            st.session_state.progress = {
                "total_questions": 25,  # 추정치
                "answered": 0,
                "percentage": 0
            }
            st.session_state.summary = {}
            st.session_state.proposal = None
            st.session_state.conversation_complete = False

    @staticmethod
    def add_message(role: str, content: str):
        """대화 히스토리에 메시지 추가"""
        st.session_state.conversation_history.append({
            "role": role,  # "assistant" or "user"
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    @staticmethod
    def save_answer(phase: int, question_key: str, answer: Any):
        """답변을 저장"""
        phase_key = f"phase_{phase}"
        st.session_state.collected_data[phase_key][question_key] = answer

        # 진행률 업데이트
        SessionManager.update_progress()

    @staticmethod
    def update_progress():
        """진행률 업데이트"""
        total_answers = sum(
            len(phase_data)
            for phase_data in st.session_state.collected_data.values()
        )
        st.session_state.progress["answered"] = total_answers
        st.session_state.progress["percentage"] = (
            total_answers / st.session_state.progress["total_questions"] * 100
        )

    @staticmethod
    def update_summary(key: str, value: str):
        """요약 정보 업데이트 (사이드바 표시용)"""
        st.session_state.summary[key] = value

    @staticmethod
    def get_current_phase_data() -> Dict:
        """현재 Phase의 수집된 데이터 반환"""
        phase_key = f"phase_{st.session_state.current_phase}"
        return st.session_state.collected_data[phase_key]

    @staticmethod
    def get_all_collected_data() -> Dict:
        """모든 수집된 데이터 반환"""
        return st.session_state.collected_data

    @staticmethod
    def move_to_next_phase():
        """다음 Phase로 이동"""
        if st.session_state.current_phase < 5:
            st.session_state.current_phase += 1
            st.session_state.current_question = 0
        else:
            st.session_state.conversation_complete = True

    @staticmethod
    def reset_conversation():
        """대화 초기화"""
        st.session_state.clear()
        SessionManager.initialize()

    @staticmethod
    def get_context_for_ai() -> Dict:
        """AI에게 전달할 컨텍스트 구성"""
        return {
            "current_phase": st.session_state.current_phase,
            "collected_data": SessionManager._flatten_collected_data(),
            "last_question": SessionManager._get_last_question(),
            "last_answer": SessionManager._get_last_answer()
        }

    @staticmethod
    def _flatten_collected_data() -> Dict:
        """Phase별로 나뉜 데이터를 평탄화"""
        flattened = {}
        for phase_data in st.session_state.collected_data.values():
            flattened.update(phase_data)
        return flattened

    @staticmethod
    def _get_last_question() -> str:
        """마지막 assistant 메시지 (질문) 반환"""
        for msg in reversed(st.session_state.conversation_history):
            if msg["role"] == "assistant":
                return msg["content"]
        return ""

    @staticmethod
    def _get_last_answer() -> str:
        """마지막 user 메시지 (답변) 반환"""
        for msg in reversed(st.session_state.conversation_history):
            if msg["role"] == "user":
                return msg["content"]
        return ""

    @staticmethod
    def is_complete() -> bool:
        """대화가 완료되었는지 확인"""
        return st.session_state.get("conversation_complete", False)

    @staticmethod
    def get_progress_percentage() -> float:
        """진행률 퍼센티지 반환"""
        return st.session_state.progress.get("percentage", 0)

    @staticmethod
    def get_summary() -> Dict:
        """요약 정보 반환"""
        return st.session_state.summary
