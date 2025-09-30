# 명탐정 코난 Quiz Agents (확장 서비스)

## 파이썬 가상환경 구성

### 1. venv 가상환경 생성

```bash
python -m venv venv
```

※ 가상환경 구성 실패 (The virtual environment was not created successfully because ensurepip is not available.) 경우, venv 패키지 설치 후 다시 명령 실행

```bash
sudo apt install python3.12-venv
```

### 2. venv 가상환경 활성화

```bash
.\venv\Scripts\activate     # windows
source ./venv/bin/activate  # macOS/Linux
```

### 3. 의존 패키지 설치

```bash
pip install -r requirements.txt
```

## 프로젝트 폴더 구조

### 1. `main.py`

애플리케이션의 진입점 - Gradio 기반 사용자 인터페이스를 초기화하고 애플리케이션을 실행

- `quiz_agents.ui.app`에서 `build_ui` 함수 import.
- `demo.launch()`를 사용하여 Gradio 앱을 실행.

```python
from quiz_agents.ui.app import build_ui

if __name__ == "__main__":
    demo = build_ui()
    demo.launch()
```

### 2. `data/` 하위 폴더

애플리케이션에서 사용하는 정적 데이터 파일을 포함

- `applicants.json`: 지원자의 클래스, 이름, 학번, 전화번호 등의 정보
- `quizzes.json`: 퀴즈 질문(예: 객관식, 주관식), 질문 텍스트, 답변 등을 포함
- `quiz_results.db`: 퀴즈 결과를 저장하는 SQLite 데이터베이스 파일.
- `avatar_conan.png` 및 `avatar_user.png`: Gradio 챗봇 UI에서 사용되는 아바타 이미지

### 3. `quiz_agents/` 하위 폴더

애플리케이션의 핵심 모듈 - 구성 정보, 모델 클래스, LangGraph 노드, 서비스 및 UI 구성에 필요한 모듈로 구분.

#### 3.1. `config.py`

`pydantic`과 `dotenv`를 사용하여 애플리케이션 구성 정보 설정.

    - 데이터 파일 경로(`DATA_DIR`, `QUIZ_FILE`, `APPLICANT_FILE`, `DB_FILE`)를 정의.
    - OpenAI 모델 설정(`OPENAI_MODEL`, `TEMPERATURE`)을 구성.
    - `.env`에서 환경 변수를 로드.

```python
from dotenv import load_dotenv
from pydantic import BaseSettings

class Settings(BaseSettings):
    OPENAI_MODEL: str = "gpt-4o"
    QUIZ_FILE: Path = Path("data/quizzes.json")
settings = Settings()
```

#### 3.2. `models.py`

`pydantic`을 사용하여 애플리케이션 전반에서 사용되는 데이터 모델을 정의.

    - `RoleRoute`: 사용자 역할(학생, 교수, 알 수 없음).
    - `ApplicantInfo`: 지원자 세부 정보.
    - `GradingResult` 및 `FinalReport`: 퀴즈 채점 결과.
    - `ReportRequest`: 교수의 보고서 요청 양식.

#### 3.3. `nodes/` 하위 폴더

LangGraph 그래프 워크플로우를 구성하기 위한 상태 및 노드 함수 구현.

    - `state.py`: 애플리케이션 상태를 관리하는 `AppState` 클래스를 정의.
    - `routing.py`: 역할(학생, 교수, 알 수 없음)에 따라 사용자 입력을 라우팅.
    - `quiz.py`: 질문 설정, 답변 수집, 채점과 같은 퀴즈 관련 논리를 구현.
    - `report.py`: 교수용 보고서 생성(예: 순위 및 오답 분석)을 처리.
    - `graph.py`: 애플리케이션 워크플로우를 위한 노드 연결 및 상태 그래프 빌드.

#### 3.4. `services/` 하위 폴더

데이터베이스 작업, 데이터 로드 및 LLM과 상호작용하기 위한 유틸리티 기능을 제공
    - `db.py`: SQLite 데이터베이스 작업(예: 퀴즈 결과 저장 및 가져오기)을 관리.
    - `loaders.py`: JSON 파일에서 퀴즈와 지원자를 로드.
    - `llm.py`: 채점 및 역할 분류와 같은 특정 작업을 위한 OpenAI LLM을 구성.

#### 3.5. `ui/` 하위 폴더

애플리케이션의 사용자 인터페이스 구성 요소를 처리.
    - `app.py`: Gradio 기반 챗봇 UI를 정의하고 이를 상태 그래프와 통합.
    - `state.py`: UI를 위한 애플리케이션 상태를 초기화.

### 4. 요약

`src` 폴더는 구성, 데이터 모델링, 워크플로우 논리, 서비스 및 UI를 처리하기 위한 모듈식 구성 요소로 구성하여 애플리케이션의 유지 관리 및 확장성을 보장.