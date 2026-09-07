#!/usr/bin/env python3
"""
ARCH metadata validator.

Implements the structural + semantic checks described in
31-ARCH-META-SCHEMA §Validation Rules, and is what `arch session commit`
(Codegen CLI Design §6.2) is specified to run before any merge to main.

No external dependencies (no jsonschema lib) — this is a small, purpose-built
validator that checks exactly what ARCH's schemas define, plus cross-file
semantic checks a generic schema validator can't do on its own (e.g. "does
this domain model reference an entity that actually exists").

Exit code 0 = commit would pass. Exit code 1 = commit would be aborted,
branch untouched, per constitution rule 5.

v2 (2026-09-06): extends the entity/workflow/integration checks below with
five backward-compatible additions from the Portfolio Engine capability-test
spike — entity `relations`, entity `key`, computed attributes, a workflow
`stateless` escape hatch, and recursive integration request/response shapes
(TypeRef). Every existing file shape continues to validate exactly as
before. The Project Config section (0) is unchanged from the version this
was patched from.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent / "metadata"
ALLOWED_TYPES = {
    "String", "Boolean", "Integer", "Decimal", "Guid", "DateTime",
    "Money", "Percentage", "Email", "Code",
}
PASCAL = re.compile(r"^[A-Z][A-Za-z0-9]*$")
WORKFLOW_NAME = re.compile(r"^[A-Z][A-Za-z0-9]*Workflow$")

errors = []
warnings = []


def fail(msg):
    errors.append(msg)


def load(path):
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        fail(f"{path}: invalid JSON — {e}")
        return None


# ---------------------------------------------------------------------------
# 0. Project config — required, exactly one file, structural validation
#    (project.config.schema.json — the installable-materials proposal)
#    UNCHANGED by the v2 patch.
# ---------------------------------------------------------------------------
CONFIG_REQUIRED = {"project", "git", "hosting", "deployment", "capabilities"}
GIT_REQUIRED = {"remote", "default_branch"}
HOSTING_REQUIRED = {"provider", "server_host", "account_username", "domain", "document_root", "deploy_path"}
DEPLOYMENT_MECHANISMS = {"ssh-git-pull", "sftp-direct-sync", "provider-api"}
RUNTIMES = {"static-html", "php", "node"}
DATABASES = {"mysql", "none"}

config_path = ROOT / "project.config.json"
if not config_path.exists():
    fail(
        f"{config_path}: missing. Every ARCH-bootstrapped project requires a project.config.json "
        f"declaring its git remote, hosting target, deployment mechanism, and capability selection — "
        f"this is the installable-materials proposal's one mandatory file."
    )
else:
    cfg = load(config_path)
    if cfg is not None:
        missing = CONFIG_REQUIRED - cfg.keys()
        if missing:
            fail(f"{config_path}: missing required top-level field(s): {sorted(missing)}")

        git_cfg = cfg.get("git", {})
        missing_git = GIT_REQUIRED - git_cfg.keys()
        if missing_git:
            fail(f"{config_path}: git config missing field(s): {sorted(missing_git)}")

        hosting_cfg = cfg.get("hosting", {})
        missing_hosting = HOSTING_REQUIRED - hosting_cfg.keys()
        if missing_hosting:
            fail(f"{config_path}: hosting config missing field(s): {sorted(missing_hosting)}")

        deployment_cfg = cfg.get("deployment", {})
        mechanism = deployment_cfg.get("mechanism")
        if mechanism not in DEPLOYMENT_MECHANISMS:
            fail(
                f"{config_path}: deployment.mechanism '{mechanism}' not in allowed set "
                f"{sorted(DEPLOYMENT_MECHANISMS)}"
            )

        capabilities_cfg = cfg.get("capabilities", {})
        runtime = capabilities_cfg.get("runtime")
        if runtime not in RUNTIMES:
            fail(f"{config_path}: capabilities.runtime '{runtime}' not in allowed set {sorted(RUNTIMES)}")
        database = capabilities_cfg.get("database")
        if database not in DATABASES:
            fail(f"{config_path}: capabilities.database '{database}' not in allowed set {sorted(DATABASES)}")


# ---------------------------------------------------------------------------
# 1. Entities — structural validation (pass 1: collect), pass 2: cross-refs
#    v2: attributes may now also be a computed-attribute object; entities may
#    declare optional 'key' and 'relations', cross-checked in pass 2 below.
# ---------------------------------------------------------------------------
entity_names = set()
entity_attrs = {}      # name -> set of attribute names (for key/via checks)
entity_relations = {}  # name -> raw relations dict (checked in pass 2)
entity_keys = {}       # name -> raw key list (checked in pass 2)

entity_dir = ROOT / "entities"
for path in sorted(entity_dir.glob("*.json")):
    data = load(path)
    if data is None:
        continue

    name = data.get("entity")
    if not name:
        fail(f"{path}: missing required field 'entity'")
        continue

    if not PASCAL.match(name):
        fail(f"{path}: entity name '{name}' must be PascalCase (e.g. 'Todo', not 'task')")
    else:
        entity_names.add(name)

    attrs = data.get("attributes")
    attr_names = set()
    if not attrs:
        fail(f"{path}: entity '{name}' has no attributes (minProperties: 1)")
    else:
        for attr, spec in attrs.items():
            attr_names.add(attr)
            if isinstance(spec, str):
                # Original shape: a bare stored-attribute type.
                if spec not in ALLOWED_TYPES:
                    fail(
                        f"{path}: attribute '{attr}' has type '{spec}', which is not in the "
                        f"allowed primitive/domain type list ({sorted(ALLOWED_TYPES)}). "
                        f"Per 31-ARCH-META-SCHEMA, domain-specific types must be defined in "
                        f"32-ARCH-DOMAIN-MODELS before use."
                    )
            elif isinstance(spec, dict):
                # v2 shape: a computed/derived attribute.
                # {"type": <AllowedType>, "computed": "<non-empty derivation text>"}
                extra = set(spec.keys()) - {"type", "computed"}
                if extra:
                    fail(f"{path}: attribute '{attr}' (computed) has unexpected key(s) {sorted(extra)}")
                atype = spec.get("type")
                if atype not in ALLOWED_TYPES:
                    fail(
                        f"{path}: computed attribute '{attr}' has type '{atype}', which is not in "
                        f"the allowed type list ({sorted(ALLOWED_TYPES)})"
                    )
                derivation = spec.get("computed")
                if not isinstance(derivation, str) or not derivation.strip():
                    fail(
                        f"{path}: computed attribute '{attr}' must carry a non-empty 'computed' "
                        f"derivation string — an empty derivation is worse than none, same "
                        f"principle as empty invariants below."
                    )
            else:
                fail(f"{path}: attribute '{attr}' must be a type string or a computed-attribute object")
    entity_attrs[name] = attr_names

    invariants = data.get("invariants", [])
    for inv in invariants:
        if not isinstance(inv, str) or not inv.strip():
            fail(
                f"{path}: entity '{name}' has an empty or invalid invariant. "
                f"Per 32-ARCH-DOMAIN-MODELS, 'AI cannot infer rules that are not written down' "
                f"— an empty invariant is worse than none: it signals an unmade decision."
            )

    # v2: optional composite/simple key declaration — cross-referenced in pass 2.
    if "key" in data:
        entity_keys[name] = data["key"]

    # v2: optional relations — target existence is checked in pass 2, since a
    # relation may point at an entity defined in a file sorted later than this one.
    if "relations" in data:
        entity_relations[name] = data["relations"]

# Pass 2 — key and relation cross-references, now that every entity is known.
for name, key in entity_keys.items():
    if not isinstance(key, list) or not key:
        fail(f"entity '{name}': 'key' must be a non-empty array of attribute names")
        continue
    for k in key:
        if k not in entity_attrs.get(name, set()):
            fail(f"entity '{name}': key attribute '{k}' is not declared in this entity's attributes")

for name, relations in entity_relations.items():
    if not isinstance(relations, dict) or not relations:
        fail(f"entity '{name}': 'relations' must be a non-empty object")
        continue
    for rel_name, rel in relations.items():
        if not isinstance(rel, dict):
            fail(f"entity '{name}': relation '{rel_name}' must be an object")
            continue
        extra = set(rel.keys()) - {"target", "cardinality", "via"}
        missing = {"target", "cardinality", "via"} - set(rel.keys())
        if extra:
            fail(f"entity '{name}': relation '{rel_name}' has unexpected key(s) {sorted(extra)}")
        if missing:
            fail(f"entity '{name}': relation '{rel_name}' is missing required key(s) {sorted(missing)}")
            continue
        target = rel["target"]
        if target not in entity_names:
            fail(
                f"entity '{name}': relation '{rel_name}' targets '{target}', which does not "
                f"exist as a defined entity"
            )
        if rel["cardinality"] not in ("one", "many"):
            fail(f"entity '{name}': relation '{rel_name}' cardinality must be 'one' or 'many', got '{rel['cardinality']}'")
        via = rel["via"]
        if via not in entity_attrs.get(name, set()):
            fail(
                f"entity '{name}': relation '{rel_name}' via-attribute '{via}' is not declared "
                f"in this entity's own attributes"
            )

# ---------------------------------------------------------------------------
# 2. Domain models — structural + cross-reference (semantic) validation
#    UNCHANGED by the v2 patch.
# ---------------------------------------------------------------------------
domain_dir = ROOT / "domain"
for path in sorted(domain_dir.glob("*.domain.json")):
    data = load(path)
    if data is None:
        continue

    entity = data.get("entity")
    if not entity:
        fail(f"{path}: missing required field 'entity'")
    elif entity not in entity_names:
        fail(
            f"{path}: references entity '{entity}', which does not exist in "
            f"/metadata/entities. (32-ARCH-DOMAIN-MODELS is downstream of entities — "
            f"the entity must be defined first.)"
        )

    events = data.get("events", [])
    if not events:
        fail(f"{path}: domain model for '{entity}' declares no events (minItems: 1)")
    for ev in events:
        if not PASCAL.match(ev):
            fail(f"{path}: event '{ev}' must be PascalCase, past-tense (e.g. 'TodoCreated')")

# ---------------------------------------------------------------------------
# 3. Workflows — structural + state-consistency (semantic) validation
#    v2: a 'stateless: true' escape hatch for entities with no real state
#    machine (mutually exclusive with states/transitions). Incidental fix:
#    this validator never actually checked the workflow-name PascalCase +
#    "Workflow" pattern its own schema doc requires — added here since this
#    function was already being touched.
# ---------------------------------------------------------------------------
workflow_dir = ROOT / "workflows"
for path in sorted(workflow_dir.glob("*.workflow.json")):
    data = load(path)
    if data is None:
        continue

    wf_name = data.get("workflow", "")
    if not WORKFLOW_NAME.match(wf_name):
        fail(f"{path}: workflow name '{wf_name}' must be PascalCase and end in 'Workflow'")

    is_stateless = data.get("stateless", False)
    has_states_or_transitions = ("states" in data) or ("transitions" in data)

    if is_stateless and has_states_or_transitions:
        fail(f"{path}: 'stateless: true' is mutually exclusive with 'states'/'transitions'")
        continue

    if is_stateless:
        continue  # nothing more to check — this entity has no state machine to validate

    states = set(data.get("states", []))
    if len(states) < 2:
        fail(f"{path}: workflow declares fewer than 2 states (minItems: 2) — or set 'stateless: true' instead")
    states.add("None")  # implicit pre-creation state, per 41-ARCH-WORKFLOW convention
    transitions = data.get("transitions", {})

    if not transitions:
        fail(f"{path}: workflow declares no transitions")

    for name, t in transitions.items():
        frm, to = t.get("from"), t.get("to")
        if frm not in states:
            fail(f"{path}: transition '{name}' has from-state '{frm}' not in declared states")
        if to not in states:
            fail(f"{path}: transition '{name}' has to-state '{to}' not in declared states")

# ---------------------------------------------------------------------------
# 4. Integrations — structural validation
#    v2: request/response shapes are now actually type-checked, recursively,
#    instead of merely required to be *an* object. Backward compatible with
#    every existing shape: {} (empty/unspecified), a flat {"field": "Type"}
#    object, and now also a nested object and/or an {"array": <TypeRef>}
#    wrapper for list-of-record shapes.
# ---------------------------------------------------------------------------
def validate_type_ref(value, path, where):
    """A TypeRef is: an allowed primitive type name; an {"array": TypeRef}
    wrapper; or a flat object of {fieldName: TypeRef} (recursion). Returns
    nothing — appends to `errors` on any violation."""
    if isinstance(value, str):
        if value not in ALLOWED_TYPES:
            fail(f"{path}: {where} has type '{value}', not in the allowed type list ({sorted(ALLOWED_TYPES)})")
        return
    if isinstance(value, dict):
        if set(value.keys()) == {"array"}:
            validate_type_ref(value["array"], path, f"{where}[]")
            return
        if "array" in value and len(value) > 1:
            fail(f"{path}: {where} mixes 'array' with other keys — an array wrapper must be the only key")
            return
        # A flat/nested object shape: {fieldName: TypeRef, ...} — {} is valid
        # (means "no fields specified", preserved for backward compatibility
        # with endpoints that genuinely return/accept nothing).
        for k, v in value.items():
            validate_type_ref(v, path, f"{where}.{k}")
        return
    fail(f"{path}: {where} must be a type string, an object shape, or an {{'array': ...}} wrapper — got {type(value).__name__}")


integration_dir = ROOT / "integrations"
for path in sorted(integration_dir.glob("*.api.json")):
    data = load(path)
    if data is None:
        continue

    endpoints = data.get("endpoints", {})
    if not endpoints:
        fail(f"{path}: integration declares no endpoints")
    for name, ep in endpoints.items():
        if "request" not in ep or "response" not in ep:
            fail(f"{path}: endpoint '{name}' missing 'request' or 'response'")
            continue
        validate_type_ref(ep["request"], path, f"endpoint '{name}' request")
        validate_type_ref(ep["response"], path, f"endpoint '{name}' response")

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
print(f"ARCH metadata validation — {ROOT}\n")

if errors:
    print(f"COMMIT WOULD FAIL — {len(errors)} error(s):\n")
    for e in errors:
        print(f"  ✗ {e}")
    print("\nBranch remains untouched. main is unaffected. (constitution rule 5)")
    sys.exit(1)
else:
    print("COMMIT WOULD PASS — all metadata is structurally and semantically valid.")
    print("Eligible for atomic merge to main and Canonical codegen.")
    sys.exit(0)