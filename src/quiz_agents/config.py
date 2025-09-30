from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # 기본 경로
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1])

    # 모델/동작
    OPENAI_MODEL: str = "gpt-4o"
    TEMPERATURE: float = 0.5
    QUIZ_COUNT: int = 3
    QUIZ_COMMANDS: tuple[str, ...] = ("퀴즈", "퀴즈 시작")

    @computed_field
    @property
    def DATA_DIR(self) -> Path:
        path = self.BASE_DIR / "data"
        path.mkdir(parents=True, exist_ok=True) # 필요시 디렉토리 생성
        return path

    @computed_field
    @property
    def QUIZ_FILE(self) -> Path:
        return self.DATA_DIR / "quizzes.json"

    @computed_field
    @property
    def APPLICANT_FILE(self) -> Path:
        return self.DATA_DIR / "applicants.json"

    @computed_field
    @property
    def DB_FILE(self) -> Path:
        return self.DATA_DIR / "quiz_results.db"

    # class Config:
    #     env_file = ".env"
    #     extra = "ignore"
        
settings = Settings()

# 결과 확인
print(f"DATA_DIR: {settings.DATA_DIR}")
print(f"QUIZ_FILE: {settings.QUIZ_FILE}")