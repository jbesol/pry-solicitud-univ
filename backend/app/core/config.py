"""Configuración central de la aplicación (leída de variables de entorno / .env)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Sistema de Gestión de Solicitudes Universitarias"
    ENVIRONMENT: str = "development"

    # Base de datos. En producción: postgresql+psycopg2://usuario:clave@host:5432/solicitudes
    # Si no se define, se usa SQLite local para facilitar la ejecución en clase.
    DATABASE_URL: str = "sqlite:///./solicitudes.db"

    # Seguridad (JWT). Nunca dejar el valor por defecto en producción.
    JWT_SECRET_KEY: str = "dev-secret-cambiar-en-produccion"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Correo opcional (si SMTP_HOST está vacío solo se usan notificaciones internas)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "no-reply@universidad.edu.co"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
