import subprocess
from pathlib import Path


def test_evaluation_make_targets_dry_run_expected_local_commands() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        [
            "make",
            "-n",
            "backend-evaluate-3d",
            "backend-evaluate-npc",
            "backend-evaluate-local",
            "final-resources-preflight",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    assert "backend-evaluate-3d:" in makefile
    assert "backend-evaluate-npc:" in makefile
    assert "backend-evaluate-local:" in makefile
    output = result.stdout
    assert "evaluate-3d" in output
    assert "--provider local" in output
    assert "--suite default-v0" in output
    assert "--output .local/3d-evaluation-local.json" in output
    assert "evaluate-npc" in output
    assert "--tick-steps 2" in output
    assert "--output .local/npc-evaluation-local.json" in output
    assert "final-resources-preflight" in output
    assert "--output .local/final-resources-preflight.json" in output
    assert output.index("evaluate-3d") < output.rindex("evaluate-npc")
