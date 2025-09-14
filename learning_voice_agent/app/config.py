"""
Configuration Management
PATTERN: Singleton configuration with environment validation
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    twilio_account_sid: Optional[str] = Field(None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(None, env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: Optional[str] = Field(None, env="TWILIO_PHONE_NUMBER")
    
    # Database
    database_url: str = Field("sqlite:///./learning_captures.db", env="DATABASE_URL")
    
    # Redis
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    redis_ttl: int = Field(1800, env="REDIS_TTL")  # 30 minutes
    
    # Server
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    cors_origins: list = Field(["*"], env="CORS_ORIGINS")
    
    # Audio Processing
    whisper_model: str = Field("whisper-1", env="WHISPER_MODEL")
    max_audio_duration: int = Field(60, env="MAX_AUDIO_DURATION")  # seconds
    
    # Claude Configuration
    claude_model: str = Field("claude-3-haiku-20240307", env="CLAUDE_MODEL")
    claude_max_tokens: int = Field(150, env="CLAUDE_MAX_TOKENS")
    claude_temperature: float = Field(0.7, env="CLAUDE_TEMPERATURE")
    
    # Session Management
    session_timeout: int = Field(180, env="SESSION_TIMEOUT")  # 3 minutes
    max_context_exchanges: int = Field(5, env="MAX_CONTEXT_EXCHANGES")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Singleton instance
settings = Settings()