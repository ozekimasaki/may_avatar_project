from pathlib import Path

REQUIRED = [
    "00_reference/character_sheet.png",
    "00_reference/character_spec.yaml",
    "00_reference/prompts/master_v001.txt",
    "00_reference/prompts/master_repair_v001.txt",
    "00_reference/prompts/face_atlas_v001.txt",
    "01_art/candidates/avatar_base.png",
    "01_art/generation_log.csv",
    "02_seethrough/notebook/mei_see_through_v002.ipynb",
    "02_seethrough/run_seethrough.py",
    "02_seethrough/see_through_commit.txt",
    "04_inochi/creator_steps_v001.md",
    "07_reviews/gates.yaml",
    "07_reviews/schema/gate_review.schema.json",
    "08_repro/pins.yaml",
    "scripts/run_tests.py",
    "scripts/review_gate.py",
    "scripts/budget.py",
    "scripts/kie_client.py",
    "scripts/qa_master.py",
    "scripts/st_run_colab.sh",
    "scripts/install_inochi_windows.ps1",
    "docs/mei_ai_first_master_plan_v003.md",
    "docs/mei_image_generation_ai_minimal_v003.md",
    "docs/mei_ai_after_image_pipeline_v003.md",
    ".github/workflows/ci.yml",
    "README.md",
    ".env.example",
    ".cursor/skills/kie-imagegen/SKILL.md",
    ".cursor/skills/mei-master/SKILL.md",
    ".cursor/skills/mei-gate-review/SKILL.md",
]


def test_repo_layout():
    root = Path(__file__).resolve().parents[1]
    missing = [rel for rel in REQUIRED if not (root / rel).exists()]
    assert missing == []
