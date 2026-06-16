from pathlib import Path

from myth_forge_api.config import Settings, load_settings


def test_default_capture_storage_dir_stays_inside_backend_local_dir() -> None:
    expected = Path(__file__).resolve().parents[1] / ".local" / "captures"

    assert Path(Settings().capture_storage_dir) == expected
    assert Path(load_settings({}).capture_storage_dir) == expected


def test_blank_capture_storage_dir_uses_default_backend_local_dir() -> None:
    expected = Path(__file__).resolve().parents[1] / ".local" / "captures"

    assert Path(load_settings({"CAPTURE_STORAGE_DIR": ""}).capture_storage_dir) == expected


def test_default_myth_session_storage_dir_stays_inside_backend_local_dir() -> None:
    expected = Path(__file__).resolve().parents[1] / ".local" / "myth-sessions"

    assert Path(Settings().myth_session_storage_dir) == expected
    assert Path(load_settings({}).myth_session_storage_dir) == expected


def test_blank_myth_session_storage_dir_uses_default_backend_local_dir() -> None:
    expected = Path(__file__).resolve().parents[1] / ".local" / "myth-sessions"

    assert Path(load_settings({"MYTH_SESSION_STORAGE_DIR": ""}).myth_session_storage_dir) == expected


def test_load_settings_reads_print_provider_configuration() -> None:
    settings = load_settings(
        {
            "PRINT_PROVIDER": "treatstock",
            "TREATSTOCK_API_KEY": "treatstock-secret",
            "TREATSTOCK_API_BASE_URL": "https://treatstock.test",
            "SCULPTEO_API_KEY": "sculpteo-secret",
        }
    )

    assert settings.print_provider == "treatstock"
    assert settings.treatstock_api_key == "treatstock-secret"
    assert settings.treatstock_api_base_url == "https://treatstock.test"
    assert settings.sculpteo_api_key == "sculpteo-secret"


def test_load_settings_explicit_env_ignores_dotenv_file(monkeypatch) -> None:
    def fail_load_dotenv() -> None:
        raise AssertionError("load_dotenv should not run for explicit env mappings")

    monkeypatch.setattr("myth_forge_api.config.load_dotenv", fail_load_dotenv)

    settings = load_settings({"THREE_D_PROVIDER": "local"})

    assert settings.three_d_provider == "local"
    assert settings.meshy_api_key is None


def test_load_settings_skip_dotenv_env_flag_ignores_dotenv_file(
    monkeypatch,
) -> None:
    def fail_load_dotenv() -> None:
        raise AssertionError("load_dotenv should not run when PMF_SKIP_DOTENV=1")

    monkeypatch.setattr("myth_forge_api.config.load_dotenv", fail_load_dotenv)
    monkeypatch.setenv("PMF_SKIP_DOTENV", "1")
    monkeypatch.delenv("NPC_PROVIDER", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    settings = load_settings()

    assert settings.npc_provider == "local"
    assert settings.openai_api_key is None
