import yaml

from scripts.budget import count_budget
from scripts.review_gate import artifact_entries, write_review
from scripts.repo import ROOT

spec = yaml.safe_load((ROOT / "07_reviews" / "gates.yaml").read_text(encoding="utf-8"))["gates"]["RIG-MVP"]
doc = {
    "gate": "RIG-MVP",
    "spec_files": spec["spec_files"],
    "spec_sections": [str(s) for s in spec["spec_sections"]],
    "artifacts": artifact_entries(spec["required_artifacts"]),
    "tests": [
        {"id": "rig.recipe_schema", "result": "pass", "detail": "nodes/pivots/parameters"},
        {"id": "rig.required_parameters_present", "result": "pass", "detail": "physics empty"},
        {"id": "rig.mesh_no_outside_alpha", "result": "pass", "detail": "bootstrap meshes"},
        {"id": "rig.mesh_density_caps", "result": "pass", "detail": "under cap"},
        {"id": "rig.pivot_head_below_face_center", "result": "pass", "detail": "HeadRoot below FaceCenter"},
        {"id": "rig.inp_not_overwriting_without_backup", "result": "pass", "detail": "creator_steps backup"},
    ],
    "scores": {},
    "hard_fail": [],
    "soft_fail": ["working/mei_mvp.inp and Creator motion screenshots are human Stage A"],
    "budget": count_budget(),
    "spec_drift": [],
    "decision": "RETRY",
    "rollback_to": None,
    "next_gate": spec["next"],
    "reviewer": "agent",
    "human_approved": False,
    "notes": "Recipe and mesh QA are ready. Creator GUI Stage A is human. Do not PASS until Blink/Mouth/Head/Eye screenshots are in 07_reviews/reports/RIG-MVP/.",
}
print(write_review(doc))
