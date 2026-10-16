from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./admissions.db"
    staff_api_key: str = "change-me-staff-key"
    auto_reject_enabled: bool = False
    shortlist_threshold: float = 0.65
    bias_ratio_threshold: float = 1.2
    resend_api_key: str = ""
    email_from: str = "admissions@example.edu"
    openai_api_key: str = ""
    upload_dir: str = "data/uploads"

settings = Settings()
