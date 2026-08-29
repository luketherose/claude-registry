#!/usr/bin/env python3
"""Validate the claude-registry plugin marketplace against the Claude Code specification.

Gates enforced (see docs/registry/how-to-write-a-capability.md):
  1. marketplace.json / plugin.json schema and cross-consistency
  2. agent frontmatter: required fields, valid model, name == filename, no duplicates
  3. skill frontmatter: name == directory, name <= 64 chars, description <= 1024 chars
  4. SKILL.md body <= 500 lines (Anthropic progressive-disclosure guidance)
  5. reference links resolve and stay one level deep from SKILL.md
  6. ${CLAUDE_PLUGIN_ROOT} paths resolve inside the owning plugin
  7. combined subagent description budget (hard limit 15000 tokens)

Exit code 0 = pass, 1 = errors found.
"""
import json, glob, os, re, sys, argparse

RESERVED_MARKETPLACES = {"claude-code-marketplace", "claude-code-plugins",
                         "anthropic-marketplace", "anthropic-plugins", "first-party-plugins"}
VALID_MODELS = {"sonnet", "opus", "haiku", "fable", "inherit"}
VALID_EFFORT = {"low", "medium", "high", "xhigh", "max"}
# Anthropic documents a 15000-token ceiling on combined custom subagent descriptions.
# Gate at 13000 to leave room for subagents the user enables from other marketplaces.
BUDGET_FAIL, BUDGET_WARN = 15000, 13000

# Measure with a real tokenizer when one is available. The word-count heuristic that
# preceded this underestimated by 17% on these descriptions, because they are dense
# with backticks, escaped quotes and technical terms that tokenize worse than prose.
# That error is why a pre-migration budget of 17018 tokens, already 2018 over the
# platform ceiling, was reported as 14246 and read as comfortably under it.
# 4.67 characters per token is calibrated against tiktoken on this corpus.
CHARS_PER_TOKEN = 4.67

try:
    import tiktoken
    _ENC = tiktoken.get_encoding("cl100k_base")
except Exception:
    _ENC = None


def count_tokens(text):
    if _ENC is not None:
        return len(_ENC.encode(text))
    return int(len(text) / CHARS_PER_TOKEN)
SKILL_BODY_MAX_LINES = 500

# Capabilities this registry has retired or renamed, with what to use instead.
# Add an entry here whenever a capability is removed, so stale references fail CI
# rather than becoming dangling dispatch instructions at runtime.
RETIRED = {
    "code-reviewer":
        "Removed 2026-08; superseded by pr-review-toolkit from the official "
        "Anthropic marketplace. State the dependency as optional.",
    "test-data-design-standards":
        "Merged 2026-05 into `test-data-seeding-standards`.",
    "database-migration-patterns":
        "Merged 2026-05 into `test-data-seeding-standards`.",
    "developer-java-spring":
        "Renamed 2026-08 to `developer-java`.",
}

errors, warnings = [], []


def err(m):
    errors.append(m)


def warn(m):
    warnings.append(m)


def split_frontmatter(path):
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    return text[3:end], text[end + 4:]


def field(fm, name):
    m = re.search(r"^%s:\s*(.*?)(?=\n[a-zA-Z_-]+:|\Z)" % name, fm, re.M | re.S)
    return m.group(1).strip() if m else None


def validate_manifests():
    mk_path = ".claude-plugin/marketplace.json"
    if not os.path.isfile(mk_path):
        err("missing .claude-plugin/marketplace.json")
        return
    mk = json.load(open(mk_path))
    for key in ("name", "owner", "plugins"):
        if key not in mk:
            err("marketplace.json: missing required field '%s'" % key)
    if not re.match(r"^[a-z0-9-]+$", mk.get("name", "")):
        err("marketplace.json: name must be kebab-case")
    if mk.get("name") in RESERVED_MARKETPLACES:
        err("marketplace.json: '%s' is a reserved marketplace name" % mk["name"])
    if "name" not in mk.get("owner", {}):
        err("marketplace.json: owner.name is required")
    names = [p.get("name") for p in mk.get("plugins", [])]
    if len(names) != len(set(names)):
        err("marketplace.json: duplicate plugin names")
    for entry in mk.get("plugins", []):
        name, src = entry.get("name"), entry.get("source")
        if not src:
            err("%s: missing source" % name)
            continue
        if not isinstance(src, str):
            continue
        if not src.startswith("./"):
            err("%s: relative source must start with ./" % name)
        if ".." in src:
            err("%s: source escapes the marketplace root" % name)
        if not os.path.isdir(src):
            err("%s: source directory %s does not exist" % (name, src))
            continue
        manifest = os.path.join(src, ".claude-plugin", "plugin.json")
        if not os.path.isfile(manifest):
            err("%s: missing %s" % (name, manifest))
            continue
        d = json.load(open(manifest))
        for key in ("name", "description", "version"):
            if key not in d:
                err("%s: plugin.json missing '%s'" % (name, key))
        if d.get("name") != name:
            err("%s: plugin.json declares name '%s'" % (name, d.get("name")))
        if not re.match(r"^\d+\.\d+\.\d+", d.get("version", "")):
            err("%s: version '%s' is not semver" % (name, d.get("version")))
        for key in ("mcpServers", "hooks"):
            value = d.get(key)
            if isinstance(value, str) and not os.path.isfile(os.path.join(src, re.sub(r"^\./", "", value))):
                err("%s: plugin.json %s points at missing %s" % (name, key, value))


def validate_agents():
    seen, per_plugin = {}, {}
    for path in sorted(glob.glob("plugins/*/agents/**/*.md", recursive=True)):
        plugin = path.split("/")[1]
        per_plugin.setdefault(plugin, 0)
        fm, body = split_frontmatter(path)
        if fm is None:
            err("%s: missing or malformed YAML frontmatter" % path)
            continue
        name = field(fm, "name")
        if not name:
            err("%s: missing 'name'" % path)
            continue
        if name.startswith("-") or ":" in name:
            err("%s: invalid name '%s'" % (path, name))
        if name != os.path.basename(path)[:-3]:
            err("%s: name '%s' does not match filename" % (path, name))
        if name in seen:
            err("duplicate agent name '%s': %s and %s" % (name, path, seen[name]))
        seen[name] = path
        desc = field(fm, "description")
        if not desc:
            err("%s: missing 'description'" % path)
        else:
            per_plugin[plugin] += count_tokens(desc)
        model = field(fm, "model")
        if model and model not in VALID_MODELS and not model.startswith("claude-"):
            err("%s: invalid model '%s'" % (path, model))
        effort = field(fm, "effort")
        if effort and effort not in VALID_EFFORT:
            err("%s: invalid effort '%s'" % (path, effort))
        if "## When to invoke" not in body:
            warn("%s: no '## When to invoke' section in the body" % path)
        # An agent told to load a skill must actually hold the Skill tool. Without it
        # the instruction is inert and the agent silently substitutes its own priors
        # for the team standard, with no error surfaced anywhere.
        tools = field(fm, "tools")
        # Keying this on a literal "## Skills" heading missed developer-frontend,
        # which routes to skills from "Invoke the framework skill set" instead.
        # Match how the body actually talks about skills, not one heading spelling.
        invokes_skill = re.search(
            r"`Skill`|Skill tool|[Ii]nvoke the [^\n]{0,40}skill", body)
        if invokes_skill and tools and "Skill" not in [
                x.strip() for x in tools.split(",")]:
            err("%s: body invokes skills but 'Skill' is missing from tools" % path)
    return per_plugin



def validate_frontmatter_yaml():
    """Every frontmatter must survive a real YAML parse.

    split_frontmatter() hands back raw text and field() reads it line by line,
    so a description with broken quoting still yields a plausible value here
    while Claude Code drops every field but the filename-derived name at load
    time. Only an actual parse catches that.
    """
    try:
        import yaml
    except ImportError:
        err("PyYAML is not installed: the frontmatter parse gate cannot run. "
            "Add 'pip install pyyaml' to the workflow.")
        return
    for path in sorted(glob.glob("plugins/**/*.md", recursive=True)):
        text = open(path, encoding="utf-8").read()
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end == -1:
            continue
        try:
            parsed = yaml.safe_load(text[3:end])
        except Exception as exc:
            err("%s: frontmatter is not valid YAML (%s). At load time every "
                "field but the name is silently dropped."
                % (path, str(exc).split("\n")[0]))
            continue
        if not isinstance(parsed, dict):
            err("%s: frontmatter does not parse to a mapping" % path)



def validate_mcp_pins():
    """MCP server specs must name a version, not a moving target.

    `npx @playwright/mcp@latest` and `uvx --from git+https://...` with no ref
    both execute whatever the upstream publishes at launch. The plugin-level
    configs were pinned; the root one was not, so the same server ran pinned or
    unpinned depending on which config won.
    """
    for path in ['.mcp.json'] + sorted(glob.glob('plugins/*/.mcp.json')):
        if not os.path.exists(path):
            continue
        try:
            config = json.load(open(path, encoding='utf-8'))
        except Exception as exc:
            err("%s: not valid JSON (%s)" % (path, exc))
            continue
        for name, spec in (config.get('mcpServers') or {}).items():
            for arg in spec.get('args', []):
                if arg.endswith('@latest') or arg in ('latest',):
                    err("%s: server '%s' pulls %s at launch; pin a version"
                        % (path, name, arg))
                if arg.startswith('git+') and '@' not in arg.split('github.com', 1)[-1]:
                    err("%s: server '%s' runs the default branch of %s; pin a "
                        "commit SHA or tag" % (path, name, arg))



def validate_cross_plugin_references():
    """A references/ path must resolve inside its own plugin, or name its owner.

    Plugins are installed independently, so a relative path can never reach
    another plugin's tree. Four replatforming supervisors point at a file owned
    by `deliberation`; that is fine only because the line says so in words. A
    bare path there would be unresolvable for both the agent and the reader.
    """
    owner = re.compile(r"the `[a-z0-9-]+` plugin")
    link = re.compile(r"[`(]\.?/?(references/[A-Za-z0-9._/-]+\.md)[`)]")
    for path in sorted(glob.glob("plugins/*/agents/**/*.md", recursive=True)
                       + glob.glob("plugins/*/skills/*/SKILL.md")):
        plugin_root = "/".join(path.split("/")[:2])
        for i, line in enumerate(open(path, encoding="utf-8"), 1):
            for m in link.finditer(line):
                rel = m.group(1)
                if os.path.exists(os.path.join(os.path.dirname(path), rel)) or \
                        os.path.exists(os.path.join(plugin_root, rel)):
                    continue
                if owner.search(line):
                    continue
                err("%s:%d: `%s` resolves in neither this file's directory nor "
                    "%s, and the line does not say which plugin owns it"
                    % (path, i, rel, plugin_root))



def validate_evals():
    """Eval files must keep one shape, and negatives must not leak the answer.

    Two schemas coexisted here once (16 scenarios as id/prompt/expectations vs
    63 as agent/query/files/expected_behavior). Separately, the `description`
    field named the routing winner on 364 of 365 cases, which let a nine-line
    keyword table score 232 out of 232 without reading anything.
    """
    verdict = re.compile(r"primary invocation|should not activate|should activate"
                         r"|route[sd]? to|belongs to|use \w+ instead", re.I)
    for path in sorted(glob.glob("plugins/*/evals/*/triggers.json")):
        try:
            cases = json.load(open(path, encoding="utf-8"))
        except Exception as exc:
            err("%s: not valid JSON (%s)" % (path, exc))
            continue
        if not isinstance(cases, list):
            err("%s: must be a flat list of cases, matching Anthropic's "
                "trigger_eval.json convention" % path)
            continue
        for i, case in enumerate(cases):
            if set(case) != {"query", "should_trigger", "description"}:
                err("%s[%d]: keys are %s, expected query, should_trigger, "
                    "description" % (path, i, sorted(case)))
            elif verdict.search(case["description"]):
                err("%s[%d]: the description states the verdict (%r). It must "
                    "describe the query only, or the case grades itself."
                    % (path, i, case["description"][:60]))

    for path in sorted(glob.glob("plugins/*/evals/*/evals.json")):
        try:
            scenarios = json.load(open(path, encoding="utf-8"))
        except Exception as exc:
            err("%s: not valid JSON (%s)" % (path, exc))
            continue
        for i, sc in enumerate(scenarios):
            if set(sc) != {"agent", "query", "files", "expected_behavior"}:
                err("%s[%d]: keys are %s, expected agent, query, files, "
                    "expected_behavior" % (path, i, sorted(sc)))
                continue
            # Fixture paths are relative to the eval directory, not the root.
            for f in sc["files"]:
                if not os.path.exists(os.path.join(os.path.dirname(path), f)):
                    err("%s[%d]: fixture %s does not exist" % (path, i, f))



def validate_workflow_dag():
    """bmad/design/workflow-dag-draft.json must list exactly the agents on disk.

    It drifted silently: two entries named capabilities removed months earlier
    while the two superseded supervisors that do exist were absent, and the
    totals matched by coincidence, so a count check would have passed.
    """
    path = "bmad/design/workflow-dag-draft.json"
    if not os.path.exists(path):
        return
    try:
        dag = json.load(open(path, encoding="utf-8"))
    except Exception as exc:
        err("%s: not valid JSON (%s)" % (path, exc))
        return
    listed = {a.get("name") for a in dag.get("agents", [])}
    on_disk = {os.path.basename(p)[:-3]
               for p in glob.glob("plugins/*/agents/**/*.md", recursive=True)}
    for name in sorted(listed - on_disk):
        err("%s: lists `%s`, which is not an agent in the tree" % (path, name))
    for name in sorted(on_disk - listed):
        err("%s: does not list `%s`, which is an agent in the tree"
            % (path, name))



# Findings the structural gates never covered. Every one of these was a real
# defect found by auditing against Anthropic's rubrics, not a hypothetical.
# They start as warnings so the backlog can be worked down, then become errors.
AGENT_BODY_MAX_CHARS = 10000
SKILL_SPLIT_HINT_LINES = 400
REFERENCE_TOC_LINES = 100


def validate_substance():
    for path in sorted(glob.glob("plugins/*/skills/*/SKILL.md")):
        body = split_frontmatter(path)[1]
        skill_dir = os.path.dirname(path)
        lines = body.count("\n")
        if lines > SKILL_SPLIT_HINT_LINES and not os.path.isdir(
                os.path.join(skill_dir, "references")):
            warn("%s: %d-line body with no references/. The 500-line gate is a "
                 "ceiling, not a target; split the detail out." % (path, lines))
        # Routing happens on the description alone. A "when to use" section in
        # the body is unreachable at that moment and only duplicates it.
        for i, line in enumerate(body.splitlines(), 1):
            if re.match(r"^#+ .*[Ww]hen (to|NOT to|not to) use", line):
                warn("%s:%d: trigger conditions belong in the description, "
                     "which is what the model routes on" % (path, i))

    for path in sorted(glob.glob("plugins/*/references/**/*.md", recursive=True)
                       + glob.glob("plugins/*/skills/*/references/**/*.md",
                                   recursive=True)):
        text = open(path, encoding="utf-8").read()
        n = text.count("\n")
        if n > REFERENCE_TOC_LINES and not re.search(r"^#+ Contents", text, re.M):
            warn("%s: %d lines with no '## Contents'. Claude previews long "
                 "files head-first and acts on a partial read." % (path, n))

    for path in sorted(glob.glob("plugins/*/agents/**/*.md", recursive=True)):
        fm, body = split_frontmatter(path)
        if fm is None:
            continue
        if len(body) > AGENT_BODY_MAX_CHARS:
            warn("%s: agent body is %d characters, over the %d ceiling"
                 % (path, len(body), AGENT_BODY_MAX_CHARS))
        # Opus is the expensive, non-default choice, so it carries its reason
        # in the file. The sonnet worker default is a class policy stated once
        # per plugin rather than repeated across 43 files.
        if field(fm, "model") == "opus" and "<!--" not in body:
            warn("%s: pins model opus with no justification comment in the body"
                 % path)


def validate_skills():
    seen = {}
    for path in sorted(glob.glob("plugins/*/skills/*/SKILL.md")):
        directory = os.path.basename(os.path.dirname(path))
        fm, body = split_frontmatter(path)
        if fm is None:
            err("%s: missing or malformed YAML frontmatter" % path)
            continue
        name = field(fm, "name")
        if not name:
            err("%s: missing 'name'" % path)
        elif name != directory:
            err("%s: name '%s' does not match directory '%s'" % (path, name, directory))
        elif len(name) > 64:
            err("%s: name exceeds 64 characters" % path)
        elif not re.match(r"^[a-z0-9-]+$", name):
            err("%s: name must be lowercase alphanumeric with hyphens" % path)
        elif any(word in name for word in ("anthropic", "claude")):
            err("%s: name contains a reserved word" % path)
        desc = field(fm, "description")
        if not desc:
            err("%s: missing 'description'" % path)
        elif len(desc) > 1024:
            err("%s: description is %d characters (max 1024)" % (path, len(desc)))
        for banned in ("model", "tools", "color"):
            if field(fm, banned) is not None:
                err("%s: '%s' is not a SKILL.md frontmatter field" % (path, banned))
        n_lines = len(body.splitlines())
        if n_lines > SKILL_BODY_MAX_LINES:
            err("%s: body is %d lines (max %d); move detail into references/"
                % (path, n_lines, SKILL_BODY_MAX_LINES))
        if name in seen:
            err("duplicate skill '%s'" % name)
        seen[name] = path
        for link in re.findall(r"\]\(([^)]+)\)", body):
            if link.startswith(("http", "#", "$", "mailto:")):
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(path), link))
            if not os.path.isfile(target):
                err("%s: broken link -> %s" % (path, link))
            elif link.count("/") > 1:
                warn("%s: reference is more than one level deep -> %s" % (path, link))


def validate_plugin_root_refs():
    for path in sorted(glob.glob("plugins/**/*.md", recursive=True)):
        root = "plugins/" + path.split("/")[1]
        text = open(path, encoding="utf-8").read()
        for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9/._-]+)", text):
            target = os.path.join(root, ref.rstrip(".,;:`)"))
            if not os.path.exists(target):
                err("%s: ${CLAUDE_PLUGIN_ROOT}/%s does not resolve" % (path, ref))


def validate_relative_links():
    """Every relative markdown link inside a plugin must resolve.

    Agent bodies and reference files carry links written as [`x.md`](../../docs/x.md),
    a form that predates the plugin layout. They are invisible to the
    ${CLAUDE_PLUGIN_ROOT} check because they contain no such variable, and they were
    the source of 84 dangling read instructions after the plugin migration.
    """
    pattern = re.compile(r"\]\((\.\.?/[A-Za-z0-9/._-]+\.md)\)|`(\.\./[A-Za-z0-9/._-]+\.md)`")
    for path in sorted(glob.glob("plugins/**/*.md", recursive=True)):
        directory = os.path.dirname(path)
        for match in pattern.finditer(open(path, encoding="utf-8").read()):
            rel = match.group(1) or match.group(2)
            if not os.path.exists(os.path.normpath(os.path.join(directory, rel))):
                err("%s: relative link does not resolve -> %s" % (path, rel))


def validate_agent_references():
    """Flag references to capabilities this registry has retired or renamed.

    Detecting every unknown name produces false positives on mode words and CLI
    verbs. Seeding the check from the retirement history is exact: it catches the
    one regression class that matters, a capability removed or renamed while
    references to it were left behind.
    """
    # Scanning only plugins/ let retired names survive in exactly the files the
    # team reads first: the wiki pages and docs/ still listed capabilities that
    # no longer exist. The changelog and archive are exempt because recording a
    # removal necessarily names the thing removed.
    scanned = (glob.glob("plugins/**/*.md", recursive=True)
               + glob.glob("wiki/*.md")
               + glob.glob("bmad/**/*.json", recursive=True)
               + glob.glob("bmad/**/*.md", recursive=True)
               + glob.glob("docs/**/*.md", recursive=True)
               + ["README.md", "CLAUDE.md"])
    exempt = ("docs/registry/CHANGELOG.md", "docs/language-agnostic-design.md",
              "docs/modernization/")
    scanned = [p for p in scanned
               if os.path.exists(p) and not any(x in p for x in exempt)]
    for name, guidance in RETIRED.items():
        # Backticks in prose, double quotes in JSON. bmad/workflows.json listed
        # two retired agents for weeks because the gate only looked for the
        # markdown spelling.
        pattern = re.compile(r'[`"]%s[`"]' % re.escape(name))
        for path in sorted(scanned):
            text = open(path, encoding="utf-8").read()
            for i, line in enumerate(text.splitlines(), 1):
                if pattern.search(line):
                    err("%s:%d: references retired capability `%s`. %s"
                        % (path, i, name, guidance))


def report(per_plugin, out, only=None):
    total_tokens = sum(per_plugin.values())
    total_agents = len(glob.glob("plugins/*/agents/**/*.md", recursive=True))
    title = {"manifests": "Marketplace validation",
             "capabilities": "Catalog validation"}.get(only, "Registry validation")
    marker = "<!-- claude-registry-validation-%s -->" % (only or "all")
    lines = [marker, "## " + title, ""]
    if not per_plugin:
        lines.append("**Errors: %d | Warnings: %d**" % (len(errors), len(warnings)))
        lines.append("")
        for e in errors:
            lines.append("- ERROR: %s" % e)
        for w in warnings:
            lines.append("- warn: %s" % w)
        text = "\n".join(lines) + "\n"
        print(text)
        if out:
            open(out, "w", encoding="utf-8").write(text)
        return
    lines += ["### Subagent description budget", "",
              "| plugin | agents | description tokens |", "|---|---:|---:|"]
    if _ENC is None:
        lines.insert(3, "> tiktoken not installed: token counts are estimated from "
                        "character length and may be off by a few percent.\n")
    for key in sorted(per_plugin, key=lambda x: -per_plugin[x]):
        count = len(glob.glob("plugins/%s/agents/**/*.md" % key, recursive=True))
        lines.append("| `%s` | %d | %d |" % (key, count, per_plugin[key]))
    lines.append("| **all enabled** | **%d** | **%d** |" % (total_agents, total_tokens))
    lines.append("")
    if total_tokens > BUDGET_FAIL:
        err("combined description budget is %d tokens (hard limit %d)" % (total_tokens, BUDGET_FAIL))
    elif total_tokens > BUDGET_WARN:
        warn("combined description budget is %d tokens (soft limit %d)" % (total_tokens, BUDGET_WARN))
    lines.append("**Errors: %d | Warnings: %d**" % (len(errors), len(warnings)))
    lines.append("")
    for e in errors:
        lines.append("- ERROR: %s" % e)
    for w in warnings:
        lines.append("- warn: %s" % w)
    text = "\n".join(lines) + "\n"
    print(text)
    if out:
        open(out, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-file")
    parser.add_argument("--only", choices=["manifests", "capabilities"],
                        help="Run only one half of the validation. "
                             "'manifests' checks marketplace.json and every plugin.json; "
                             "'capabilities' checks agents, skills, references and the "
                             "description budget. Omit to run both.")
    args = parser.parse_args()
    budget = {}
    if args.only in (None, "manifests"):
        validate_manifests()
        validate_mcp_pins()
    if args.only in (None, "capabilities"):
        validate_frontmatter_yaml()
        validate_evals()
        validate_workflow_dag()
        validate_substance()
        validate_cross_plugin_references()
        budget = validate_agents()
        validate_skills()
        validate_plugin_root_refs()
        validate_relative_links()
        validate_agent_references()
    report(budget, args.output_file, args.only)
    sys.exit(1 if errors else 0)
