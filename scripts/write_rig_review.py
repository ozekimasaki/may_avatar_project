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
        {"id": "rig.inx_is_creator_v086", "result": "pass", "detail": "may.inx TRNSRTS v0.8.6; params empty"},
    ],
    "scores": {},
    "hard_fail": [],
    "soft_fail": [
        "may.inx has PSD parts under Root; HeadRoot/NeckRoot hierarchy not built",
        "param is null; EyeOpen/Mouth/Head/EyeBall missing",
        "Creator Blink/Mouth/Head/Eye screenshots missing",
    ],
    "budget": count_budget(),
    "spec_drift": [],
    "decision": "RETRY",
    "rollback_to": None,
    "next_gate": spec["next"],
    "reviewer": "agent",
    "human_approved": False,
    "notes": "Recipe, meshes, and imported may.inx exist. Stage A node/parameter/texture/screenshot steps are human Creator GUI. Do not invent INX. Do not PASS until blink.png mouth.png head.png eyes.png are in 07_reviews/reports/RIG-MVP/.",
}
print(write_review(doc))
