"""Small static design review inspired by the teacher's Unit 1 design-review notebook."""

def audit_tools(schema, registry):
    findings = []
    schema_names = []
    for item in schema:
        fn = item.get("function", {})
        name = fn.get("name")
        schema_names.append(name)
        if name not in registry:
            findings.append(f"ERROR {name}: schema tool is missing from REGISTRY")
        desc = fn.get("description", "")
        if len(desc) < 50:
            findings.append(f"WARNING {name}: tool description is too short")
        params = fn.get("parameters", {})
        properties = params.get("properties", {})
        required = set(params.get("required", []))
        for p in required:
            if p not in properties:
                findings.append(f"ERROR {name}: required parameter '{p}' is not declared")
            elif not properties[p].get("description"):
                findings.append(f"WARNING {name}.{p}: parameter has no description")

    for name in registry:
        if name not in schema_names:
            findings.append(f"WARNING {name}: registry tool is invisible to the model")
    return findings


def audit_guards(max_steps, has_whitelist, retries, validates_output, has_memory):
    findings = []
    if max_steps <= 0:
        findings.append("ERROR: no positive step budget")
    if not has_whitelist:
        findings.append("ERROR: no registry/whitelist check")
    if retries < 0:
        findings.append("ERROR: invalid retry policy")
    if not validates_output:
        findings.append("WARNING: tool output is not validated")
    if not has_memory:
        findings.append("ERROR: no session memory")
    return findings
