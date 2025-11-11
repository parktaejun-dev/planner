# 🎨 AI 마케팅 컨설턴트 - 민준

20년 경력 광고 전문가 페르소나와 1:1 대화를 통해 맞춤형 마케팅 전략을 제안받는 Streamlit 기반 AI 서비스

## 📋 프로젝트 개요

- **서비스명**: AI 마케팅 컨설턴트
- **페르소나**: 민준 (20년 경력 광고대행사 전문가)
- **핵심 기능**:
  - 5단계 객관식 대화를 통한 체계적 정보 수집
  - AI 기반 실시간 공감 및 맥락 이해
  - 전문가 수준의 마케팅 전략 제안서 자동 생성

## 🚀 빠른 시작

### 1. 설치

```bash
pip install -r requirements.txt
```

### 2. API 키 설정

`.streamlit/secrets.toml` 파일을 수정하여 Gemini API 키를 입력하세요:

```toml
GEMINI_API_KEY = "your-actual-api-key-here"
```

**API 키 발급 방법:**
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 방문
2. API 키 생성
3. 위 파일에 복사

### 3. 실행

```bash
streamlit run app.py
```

브라우저에서 자동으로 `http://localhost:8501` 이 열립니다.

## 📂 프로젝트 구조

```
marketing-consultant-ai/
├── app.py                      # 메인 Streamlit 애플리케이션
├── requirements.txt            # 패키지 의존성
├── .streamlit/
│   ├── config.toml            # Streamlit 설정
│   └── secrets.toml           # API 키 (비공개)
├── config/
│   └── persona.py             # 민준 페르소나 & 시스템 프롬프트
├── utils/
│   ├── gemini_helper.py       # Gemini API 연동
│   └── session_manager.py     # Session State 관리
└── README.md
```

## 🎯 주요 기능

### 1. 5단계 대화 프로세스

| Phase | 주제 | 질문 수 |
|-------|------|---------|
| 1 | 라포 형성 및 비즈니스 이해 | 5개 |
| 2 | 기존 마케팅 경험 탐색 | 5개 |
| 3 | 목표 및 제약사항 조사 | 6개 |
| 4 | 타겟 고객 및 인사이트 | 5개 |
| 5 | 전략 선호 및 방향 | 4개 |

**총 25개 객관식 질문**

### 2. 객관식 위젯 종류

- **단일 선택** (Radio): 하나만 선택
- **복수 선택** (Multiselect): 여러 개 선택 가능
- **척도** (Slider): 1~10점 만족도 등

### 3. AI 역할

- **실시간 공감 멘트**: 답변에 따라 전문가처럼 반응
- **맥락 이해**: 이전 답변을 기억하고 연결
- **제안서 생성**: 수집된 정보 기반 전문가급 제안서 작성

### 4. 제안서 구성

- Executive Summary
- 비즈니스 및 시장 분석
- 마케팅 목표 및 KPI
- 전략 및 실행 방안
- 미디어 믹스 및 예산안
- 예상 성과
- 실행 로드맵
- 리스크 및 대응 방안

## 🎨 UI/UX 특징

- **깔끔한 챗 인터페이스**: 민준과 사용자 메시지 구분
- **실시간 진행률**: 사이드바에서 진행 상황 확인
- **수집 정보 요약**: 중요 정보 실시간 표시
- **원클릭 선택**: 모든 답변을 클릭만으로 완료

## 📊 사용 시나리오 예시

### 케이스 1: 비건 화장품 브랜드 신규 런칭

1. 업종: 화장품/뷰티
2. 타겟: 20~30대 여성
3. 예산: 3억원
4. 목표: 브랜드 인지도 + 온라인 판매
5. 기간: 6개월

**결과**: 인플루언서 마케팅 중심의 스토리텔링 전략 제안서 생성

### 케이스 2: 외식 프랜차이즈 확장

1. 업종: 식음료/F&B
2. 타겟: 30~40대 가족
3. 예산: 5천만원
4. 목표: 오프라인 매장 방문
5. 기간: 3개월

**결과**: 지역 기반 온·오프라인 통합 전략 제안서 생성

## 🔧 기술 스택

- **Frontend**: Streamlit
- **AI**: Google Gemini API (gemini-pro)
- **언어**: Python 3.9+
- **상태 관리**: Streamlit Session State

## ⚙️ 설정 옵션

### Streamlit 테마 커스터마이징

`.streamlit/config.toml` 에서 색상 변경 가능:

```toml
[theme]
primaryColor = "#1976D2"        # 메인 색상
backgroundColor = "#FFFFFF"      # 배경색
secondaryBackgroundColor = "#F5F5F5"  # 보조 배경색
textColor = "#262730"           # 텍스트 색상
```

## 📝 개발 로그

### MVP v1.0 (2025-11-11)

- [x] 기본 프로젝트 구조
- [x] Gemini API 연동
- [x] 5단계 25개 객관식 질문
- [x] Session State 관리
- [x] 챗 UI 구현
- [x] 제안서 자동 생성
- [x] 마크다운 다운로드

### 향후 개선 예정

- [ ] 전문 데이터 DB 연동 (업종별 ROAS, CPC)
- [ ] PDF 제안서 변환
- [ ] 예산/성과 차트 시각화
- [ ] 대화 저장/불러오기
- [ ] 다국어 지원

## 🐛 문제 해결

### API 키 오류

```
⚠️ Gemini API 키를 설정해주세요!
```

→ `.streamlit/secrets.toml` 파일에서 `GEMINI_API_KEY` 확인

### 모듈 import 오류

```bash
pip install -r requirements.txt --upgrade
```

### Streamlit 실행 안 됨

```bash
streamlit --version
# 1.30.0 이상 확인
```

## 📄 라이선스

MIT License

## 👤 개발자

AI 마케팅 컨설턴트 프로젝트 팀

## 🙏 감사의 글

- Google Gemini API
- Streamlit 커뮤니티