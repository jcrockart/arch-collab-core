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
# 1. Entities — structural validation
# ---------------------------------------------------------------------------
entity_names = set()
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
    if not attrs:
        fail(f"{path}: entity '{name}' has no attributes (minProperties: 1)")
    else:
        for attr, atype in attrs.items():
            if atype not in ALLOWED_TYPES:
                fail(
                    f"{path}: attribute '{attr}' has type '{atype}', which is not in the "
                    f"allowed primitive/domain type list ({sorted(ALLOWED_TYPES)}). "
                    f"Per 31-ARCH-META-SCHEMA, domain-specific types must be defined in "
                    f"32-ARCH-DOMAIN-MODELS before use."
                )

    invariants = data.get("invariants", [])
    for inv in invariants:
        if not isinstance(inv, str) or not inv.strip():
            fail(
                f"{path}: entity '{name}' has an empty or invalid invariant. "
                f"Per 32-ARCH-DOMAIN-MODELS, 'AI cannot infer rules that are not written down' "
                f"— an empty invariant is worse than none: it signals an unmade decision."
            )

# ---------------------------------------------------------------------------
# 2. Domain models — structural + cross-reference (semantic) validation
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
# ---------------------------------------------------------------------------
workflow_dir = ROOT / "workflows"
for path in sorted(workflow_dir.glob("*.workflow.json")):
    data = load(path)
    if data is None:
        continue

    states = set(data.get("states", []))
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
# ---------------------------------------------------------------------------
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
