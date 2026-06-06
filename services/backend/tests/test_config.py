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
