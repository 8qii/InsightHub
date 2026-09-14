import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_uses_safe_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_env == "development"
    assert settings.anythingllm_api_key is None
    assert settings.max_upload_size_mb == 100


def test_settings_rejects_invalid_environment() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="invalid", _env_file=None)


def test_settings_rejects_non_positive_upload_limit() -> None:
    with pytest.raises(ValidationError):
        Settings(max_upload_size_mb=0, _env_file=None)
