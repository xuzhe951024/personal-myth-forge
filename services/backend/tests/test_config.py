from pathlib import Path

from myth_forge_api.config import Settings, load_settings


def test_default_capture_storage_dir_stays_inside_backend_local_dir() -> None:
    expected = Path(__file__).resolve().parents[1] / ".local" / "captures"

    assert Path(Settings().capture_storage_dir) == expected
    assert Path(load_settings({}).capture_storage_dir) == expected
