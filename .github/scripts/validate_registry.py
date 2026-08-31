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

# Directories the migration removed. Separate from RETIRED because the failure is
# different: a retired NAME is wrong wherever it appears, while a retired PATH is
# expected in a record of the migration and only wrong where something follows it.
RETIRED_PATHS = {
    "claude-catalog":
        "Removed 2026-08; the development source tier no longer exists. "
        "Capabilities live at `plugins/<plugin>/`.",
    "claude-marketplace":
        "Removed 2026-08; distribution is `.claude-plugin/marketplace.json` "
        "plus one `plugin.json` per plugin.",
}

errors, warnings = [], []

# Up to three leading spaces, then a run of three or more backticks. A backtick
# inside the info string means the line is an inline code run, not a fence.
FENCE_LINE = re.compile(r"^ {0,3}(`{3,})(.*)$")


def scan_fences(text):
    """Classify every line as prose or fenced code, and find an unclosed opener.

    One model, shared, because two gates ask the same question of the same text
    and a disagreement between them exempts a region the other says is not there.

    Straight CommonMark, which is what every renderer this material passes through
    implements. A block runs until a closing fence that is bare and at least as
    long as the opener. Two consequences carry the gate. A shorter run inside a
    longer block is content, so a four-backtick block may quote a three-backtick
    opener without the quoted line meaning anything. A run carrying an info string
    can never close anything, so a ```python seen inside an open block is content
    too, and the block is still open after it.

    Blocks do not nest, and modelling them as if they did was tempting here: seven
    sites put ```mermaid or ```gherkin inside a three-backtick template. Those
    sites are miswritten rather than unsupported, since holding a three-backtick
    block needs a four-backtick fence around it, and inventing a dialect that
    accepts them buys a green build by describing a rendering nobody performs. It
    also costs the gate its subject: reading them as CommonMark does is what
    surfaces `functional-analyst.md:172`, a sixth instance of the stray fence this
    gate exists for, swallowing 54 lines including both reference links.

    Returns (context, unclosed). context[n] is None when line n+1 is prose, else
    the info string of the block holding it. unclosed is the line of an opener
    that never closes, or None.
    """
    lines = text.split("\n")
    context = [None] * len(lines)
    opener = None
    for idx, line in enumerate(lines):
        m = FENCE_LINE.match(line)
        if m and "`" not in m.group(2):
            run, info = len(m.group(1)), m.group(2).strip()
            if opener is None:
                opener = (idx + 1, run, info)
                context[idx] = info
                continue
            if run >= opener[1] and info == "":
                context[idx] = opener[2]
                opener = None
                continue
        context[idx] = opener[2] if opener else None
    return context, (opener[0] if opener else None)


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
    owner = re.compile(r"the `([a-z0-9-]+)` plugin")
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
                # Naming an owner is not enough: the named plugin has to exist
                # and the file has to be in it, or the sentence is decoration.
                m_owner = owner.search(line)
                if m_owner:
                    other = os.path.join("plugins", m_owner.group(1), rel)
                    if os.path.exists(other):
                        continue
                    err("%s:%d: names the `%s` plugin as owner of `%s`, but %s "
                        "does not exist"
                        % (path, i, m_owner.group(1), rel, other))
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
    # Listing phrasings only constrained six of them. The property is that the
    # description says what the query is about and never which capability wins,
    # so naming any capability in the registry is the thing to reject.
    capability_names = sorted(
        {os.path.basename(p)[:-3]
         for p in glob.glob("plugins/*/agents/**/*.md", recursive=True)}
        | {os.path.basename(os.path.dirname(p))
           for p in glob.glob("plugins/*/skills/*/SKILL.md")},
        key=len, reverse=True)
    phrasings = re.compile(r"primary invocation|should not activate"
                           r"|should activate|route[sd]? to|belongs to"
                           r"|use \w+ instead", re.I)

    def names_a_sibling(text, query, own):
        """The leak is routing information the query does not already carry.

        A description may repeat the subject the query names: a TanStack Start
        query described as being about TanStack Start tells a grader nothing it
        could not read off the query. Naming a capability the query never
        mentions is what hands over the answer.
        """
        for other in capability_names:
            if other == own:
                continue
            pat = r"(?<![\w-])%s(?![\w-])" % re.escape(other)
            if re.search(pat, text, re.I) and not re.search(pat, query, re.I):
                return other
        return None
    # templates/ is included: the scaffold shipped three descriptions that this
    # very gate rejects, so anyone copying it started with a red build.
    for path in sorted(glob.glob("plugins/*/evals/*/triggers.json")
                       + glob.glob("templates/**/triggers.json", recursive=True)):
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
            else:
                own = os.path.basename(os.path.dirname(path))
                sibling = names_a_sibling(case["description"],
                                          case["query"], own)
                if phrasings.search(case["description"]):
                    err("%s[%d]: the description states the verdict (%r). It "
                        "must describe the query only, or the case grades "
                        "itself." % (path, i, case["description"][:60]))
                elif sibling:
                    err("%s[%d]: the description names `%s`, which hands a "
                        "grader the answer. Describe the query, not the winner."
                        % (path, i, sibling))

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
        err("%s is missing. Deleting it must not be a way to silence this gate."
            % path)
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


def validate_code_fences():
    """Every fenced block under plugins/ closes. Structure, not parity.

    Five files carried a stray closing fence left over from an earlier edit. A
    lone ``` opens a block rather than erroring, so everything after it renders
    as code: in one SKILL.md that swallowed the quality checklist and both
    reference links. Nothing caught it, because the links still resolved as
    text and the body stayed under the line ceiling.

    Counting the markers and rejecting an odd total was wrong in both
    directions. It passed a file carrying one stray closer and one unclosed
    opener, four markers being an even number, and it failed a correct file
    where a four-backtick block documents a three-backtick opener, three markers
    being odd. Neither verdict described how the file renders. It also had no
    state, so a ``` printed by a script inside a block counted as a marker.

    scan_fences() holds the model. What stays undetectable is two stray closers
    with nothing but bare fences between them: a bare ``` is an opener or a
    closer purely by the state it lands in, so that pair is textually identical
    to one of the 266 legitimate untagged blocks here. Separating them needs a
    content heuristic, and the obvious one, a markdown heading inside an untagged
    block, fires on 34 real deliverable templates in this tree. Put one tagged
    fence between the two strays and the info-string rule catches them, which is
    the common case in any file that shows code at all.
    """
    for path in sorted(glob.glob("plugins/**/*.md", recursive=True)):
        unclosed = scan_fences(open(path, encoding="utf-8").read())[1]
        if unclosed is not None:
            err("%s:%d: this code fence opens a block that never closes. "
                "Everything below it renders as code." % (path, unclosed))


# No em dash in prose, and none in a block an agent copies into a deliverable.
EM_DASH = "\u2014"
# An untagged block and a `markdown` block are output templates, so the
# character there is punctuation this registry emits. A language-tagged block is
# a code sample, where it sits inside a comment being illustrated.
TEMPLATE_INFO = {"", "markdown", "md", "text", "txt"}


def validate_em_dash():
    """Hold plugins/**/*.md to the em dash rule CLAUDE.md states.

    The rule had no gate, which is how a convention becomes decoration. The
    scope is exactly what the tree can hold to today and no wider: across 370
    files under plugins/ the count is 0 in prose, 0 in untagged and
    `markdown`-tagged fences, and 245 inside language-tagged fences, which are
    the samples the rule already exempts.

    Left out on purpose, because gating them would fail the build on a backlog
    rather than on a regression: `plugins/**/*.json`, still carrying 32 in eval
    strings, and everything under docs/, where the changelog alone has 430.
    """
    for path in sorted(glob.glob("plugins/**/*.md", recursive=True)):
        text = open(path, encoding="utf-8").read()
        context = scan_fences(text)[0]
        for i, line in enumerate(text.split("\n"), 1):
            if EM_DASH not in line:
                continue
            info = context[i - 1]
            if info is None:
                where = "prose"
            elif (info.split() or [""])[0].lower() in TEMPLATE_INFO:
                where = "an output template block"
            else:
                continue
            err("%s:%d: em dash in %s. Use a comma, a colon, parentheses or a "
                "second sentence." % (path, i, where))


def validate_plugin_root_refs():
    """${CLAUDE_PLUGIN_ROOT} resolves, and is never left bare in agent prose.

    The bare-token half is scoped to `plugins/*/agents/` and to prose, because
    that is the only file class the installer rewrites and the only place a bare
    token does damage. `scripts/install-local.sh:112` performs the substitution
    inside the loop over `plugins/$p/agents`; skills go through `cp -R` at line
    122 and bundled references at line 96, and neither is ever touched. The old
    gate scanned every markdown file under plugins/ on a rationale that held for
    one third of them, and it cost something measurable: the `cross-host-parity`
    skill degraded its own mapping table and added a paragraph apologising for
    the degradation, to avoid spelling a variable it is documenting.

    Inside a fenced block the token is also correct and has to survive. A hooks
    or MCP snippet writes `"cwd": "${CLAUDE_PLUGIN_ROOT}"` and a shell example
    writes `cd ${CLAUDE_PLUGIN_ROOT}`; both are what Claude Code expands at run
    time, and the old advice to drop the braces would have made the snippet wrong
    the moment a reader copied it. install-local.sh rewriting fenced snippets too
    is an installer bug, not an authoring one, and the fix belongs there.

    Still an error, because it is the defect that started this: a bare token in
    agent prose. The installer drops an absolute path into the middle of a
    sentence, and when the plugin ships no references/ and no examples/ the path
    it names was never created. scripts/test-clean-install.sh:48 catches that
    case at install time; this catches it at review time.
    """
    for path in sorted(glob.glob("plugins/**/*.md", recursive=True)):
        root = "plugins/" + path.split("/")[1]
        text = open(path, encoding="utf-8").read()
        if "/agents/" in path:
            context = scan_fences(text)[0]
            for i, line in enumerate(text.split("\n"), 1):
                if context[i - 1] is not None:
                    continue
                if re.search(r"\$\{CLAUDE_PLUGIN_ROOT\}(?!/)", line):
                    err("%s:%d: leaves ${CLAUDE_PLUGIN_ROOT} bare in agent prose. "
                        "install-local.sh rewrites the token in every agent body, "
                        "so this sentence reaches the reader with an absolute path "
                        "in it, naming a directory that exists only if the plugin "
                        "ships references/ or examples/. Put a path after it, or "
                        "move the mention into a code fence." % (path, i))
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
        # Word boundaries, not just backticks and quotes. Matching only the
        # decorated spellings left bare prose through, including a dispatch
        # instruction naming an agent this registry no longer has. The
        # lookbehind excludes a colon so the official `pr-review-toolkit:`
        # replacement, which necessarily contains the retired string, is not
        # flagged as the thing it replaces.
        pattern = re.compile(r'(?<![\w:.-])%s(?![\w-])' % re.escape(name))
        for path in sorted(scanned):
            text = open(path, encoding="utf-8").read()
            for i, line in enumerate(text.splitlines(), 1):
                if pattern.search(line):
                    err("%s:%d: references retired capability `%s`. %s"
                        % (path, i, name, guidance))

    # A retired DIRECTORY is scanned over a different set than a retired name,
    # because it is not the same failure. Eight files name one and are right to:
    # `docs/registry/CHANGELOG.md`, `wiki/Changelog.md`,
    # `docs/registry/release-process.md`,
    # `docs/registry/how-to-write-a-capability.md`,
    # `templates/new-use-case/README.md` and the three `docs/modernization/w7-*`
    # audits each record the removal in the past tense, and a record has to name
    # what it removed. Exempting them one by one is how a gate becomes decoration,
    # so the scan follows execution instead of prose: capability material, the
    # workflow registry, and the maintenance scripts. `archive/` stays out for the
    # same reason the records do.
    #
    # Scripts are in the set because leaving them out is how `scripts/present.sh`
    # kept a prompt telling an agent to read
    # `claude-catalog/policies/accenture-branding.md` after the directory was
    # deleted. The glob was `*.md` plus `*.json`, so a `.sh` file was invisible
    # even inside a directory that was being scanned.
    followed = (glob.glob("plugins/**/*.md", recursive=True)
                + glob.glob("plugins/**/*.json", recursive=True)
                + glob.glob("bmad/**/*.json", recursive=True)
                + glob.glob("bmad/**/*.md", recursive=True)
                + [p for p in glob.glob("scripts/**/*", recursive=True)
                   + glob.glob("hooks/**/*", recursive=True)
                   if os.path.isfile(p)])
    for name, guidance in RETIRED_PATHS.items():
        # A trailing separator is still required, so CLAUDE.md and a plugin body
        # can both state that the directory does not exist without naming a path.
        # Either separator counts: a Windows path in a fenced example is a path.
        # The lookbehind now excludes only word characters and the hyphen, which
        # is all it takes to tell `my-claude-catalog/` from the real name. The
        # previous class also excluded `/`, `.` and `-`, which are exactly the
        # characters a path is written after, so `./claude-catalog/x`,
        # `~/dev/claude-registry/claude-catalog/x`, `../claude-catalog/x` and
        # `$ROOT/claude-catalog/x` all passed: four of the six forms that occur.
        pattern = re.compile(r'(?<![\w-])%s[/\\]' % re.escape(name))
        for path in sorted(set(followed)):
            if not os.path.exists(path):
                continue
            for i, line in enumerate(
                    open(path, encoding="utf-8", errors="replace"), 1):
                if pattern.search(line):
                    err("%s:%d: names the retired path `%s/`. %s"
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
        validate_code_fences()
        validate_em_dash()
        validate_plugin_root_refs()
        validate_relative_links()
        validate_agent_references()
    report(budget, args.output_file, args.only)
    sys.exit(1 if errors else 0)
