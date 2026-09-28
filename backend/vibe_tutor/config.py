import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

RUTA_ENV = "/etc/vibe-tutor/.env"
# Claves de los proveedores: obligatorias salvo en el modo demo, que no llama a ninguno.
CLAVES_API = ("anthropic_api_key", "gemini_api_key", "resend_api_key")


class Settings(BaseSettings):
    """Variables de /etc/vibe-tutor/.env; los nombres están en deploy/.env.example."""

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8", extra="ignore", hide_input_in_errors=True, env_ignore_empty=True
    )

    anthropic_api_key: str = Field(default="", repr=False)
    gemini_api_key: str = Field(default="", repr=False)
    resend_api_key: str = Field(default="", repr=False)
    mail_from: str = Field(min_length=1)
    turnstile_site_key: str = ""
    turnstile_secret: str = Field(default="", repr=False)
    jwt_secret: str = Field(min_length=32, repr=False)
    admin_email: str = Field(min_length=3)
    dominio: str = Field(min_length=1)
    tope_alumno_usd: float = 1.0
    tope_mensual_usd: float = 50.0
    data_dir: Path = Path("/srv/vibe-tutor/data")
    contenido_dir: Path = Path("/srv/vibe-tutor/contenido")
    dev_codigo_fijo: str | None = Field(default=None, repr=False)
    modelo: str = "claude-sonnet-5"
    tts_modelo: str = "gemini-3.8-flash-tts"
    tts_modelo_respaldo: str = "gemini-2.5-flash-preview-tts"
    tts_voz: str = "Charon"
    max_codigos_mail_hora: int = 5
    max_codigos_ip_hora: int = 20
    max_codigos_dia: int = 80
    aviso_prueba: bool = True
    tareas_activas: bool = True
    # Quien opera el curso: llena {{AUTOR}} en el contenido (vacío: "el autor del curso").
    autor_nombre: str = ""
    # Nombre de la lista de novedades por mail (vacío: no hay casilla de novedades).
    newsletter_nombre: str = ""
    # Con true el tutor responde con un guion fijo, sin llamar a Claude; la voz queda apagada, los
    # mails se registran en el log en vez de mandarse y no hacen falta claves de API.
    modo_demo: bool = False

    @field_validator("dev_codigo_fijo", mode="before")
    @classmethod
    def _vacio_es_none(cls, valor):
        if isinstance(valor, str) and not valor.strip():
            return None
        return valor

    @field_validator("autor_nombre", "newsletter_nombre")
    @classmethod
    def _sin_espacios_de_mas(cls, valor: str) -> str:
        return " ".join(valor.split())

    @property
    def hay_newsletter(self) -> bool:
        """Si el curso tiene lista de novedades: sin ella no se muestra ni se guarda esa casilla."""
        return bool(self.newsletter_nombre.strip())

    @model_validator(mode="after")
    def _claves_de_api(self) -> "Settings":
        if not self.modo_demo:
            faltan = [campo.upper() for campo in CLAVES_API if not getattr(self, campo).strip()]
            if faltan:
                raise ValueError(f"faltan {', '.join(faltan)} (obligatorias salvo con MODO_DEMO=true)")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings(_env_file=os.environ.get("VIBE_ENV_FILE", RUTA_ENV))
