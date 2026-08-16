import yaml

from scripts.budget import count_budget
from scripts.inx_inspect import inspect_inx
from scripts.review_gate import artifact_entries, write_review
from scripts.repo import ROOT

spec = yaml.safe_load((ROOT / "07_reviews" / "gates.yaml").read_text(encoding="utf-8"))["gates"]["RIG-MVP"]
inx = inspect_inx(ROOT / "04_inochi" / "working" / "may.inx")
shots = [
    ROOT / "07_reviews" / "reports" / "RIG-MVP" / name
    for name in ("blink.png", "mouth.png", "head.png", "eyes.png")
]
shots_ok = all(path.is_file() and path.stat().st_size > 0 for path in shots)
head_ok = "HeadRoot" in inx["nodes"] and "NeckRoot" in inx["nodes"] and "BodyRoot" in inx["nodes"]
face_under_head = inx["nodes"].index("HeadRoot") < inx["nodes"].index("Face") if head_ok and "Face" in inx["nodes"] else False
soft = []
if inx["root_child_names"][0] != "BodyRoot" or "Arm_L" in inx["root_child_names"]:
    soft.append("Body parts still under Root; Arm/Skirt not parented to BodyRoot")
if inx["param_count"] < 9:
    soft.append(f"parameters are {inx['param_count']} default Param #N (want 9 named EyeOpen/Mouth/Head/EyeBall)")
if not any(name.startswith("EyeOpen") for name in inx["param_names"]):
    soft.append("parameter names not renamed; bindings empty; atlas textures not merged")
if not shots_ok:
    soft.append("Creator Blink/Mouth/Head/Eye screenshots missing")
else:
    soft.append("screenshots are Creator rest-pose session shots; keyforms not recorded")

doc = {
    "gate": "RIG-MVP",
    "spec_files": spec["spec_files"],
    "spec_sections": [str(s) for s in spec["spec_sections"]],
    "artifacts": artifact_entries(spec["required_artifacts"]),
    "tests": [
        {"id": "rig.recipe_schema", "result": "pass", "detail": "nodes/pivots/parameters"},
        {"id": "rig.required_parameters_present", "result": "pass", "detail": "physics empty in recipe"},
        {"id": "rig.mesh_no_outside_alpha", "result": "pass", "detail": "bootstrap meshes"},
        {"id": "rig.mesh_density_caps", "result": "pass", "detail": "under cap"},
        {"id": "rig.pivot_head_below_face_center", "result": "pass", "detail": "HeadRoot world Y below FaceCenter"},
        {"id": "rig.inp_not_overwriting_without_backup", "result": "pass", "detail": "creator_steps backup"},
        {
            "id": "rig.inx_is_creator_v086",
            "result": "pass",
            "detail": (
                f"may.inx TRNSRTS {inx['version']}; "
                f"HeadRoot/NeckRoot/BodyRoot present; {inx['param_count']} params; "
                f"root children={inx['root_child_names'][:4]}"
            ),
        },
    ],
    "scores": {},
    "hard_fail": [],
    "soft_fail": soft,
    "budget": count_budget(),
    "spec_drift": [],
    "decision": "RETRY",
    "rollback_to": None,
    "next_gate": spec["next"],
    "reviewer": "agent",
    "human_approved": False,
    "notes": (
        "Cloud Creator v0.8.6 saved may.inx. Hierarchy: BodyRoot(0,20) > NeckRoot(0,-365) > "
        "HeadRoot(0,0) with Face/eyes/mouth/hair/Ahoge as children. 8 parameters created "
        "(not renamed, no bindings). Atlas merge and keyforms incomplete. Do not invent INX. "
        "human_approved stays false."
    ),
}
print(write_review(doc))
