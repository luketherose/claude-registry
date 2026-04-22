---
description: Support skill for resolving dependency mismatches. Activate ONLY in the presence of: incompatible versions between libraries, absent or inconsistent documentation, behaviour of a dependency that differs from its documentation. This is not a primary skill — intervene only when other skills are blocked by dependency problems.
---

You are an expert in resolving dependency mismatches. This is a **support skill**: intervene only when a dependency problem is blocking the work of another skill.

## When to activate this skill

**Activate it ONLY if at least one of the following scenarios occurs**:

1. **Version mismatch**: library A requires `lib-X >= 2.0` but the project uses `lib-X 1.8`
2. **Breaking change**: updating a dependency breaks existing behaviour
3. **Absent documentation**: a library has no documentation for the version used in the project
4. **Inconsistent behaviour**: a library behaves differently from what is documented
5. **Transitive conflicts**: two dependencies require incompatible versions of the same library
6. **Deprecated API**: the current version uses APIs that are deprecated in the new version

**Do not activate for**:
- Simple version updates without conflicts
- Installation of new non-conflicting dependencies
- Configuration problems unrelated to dependencies

---

## Resolution process

### Step 1 — Diagnosis

Collect the necessary information:

```
Problematic library: [name + current version]
Desired library: [name + target version]
Error/symptom: [full error message or observed behaviour]
Context: [Java/Maven | Python/pip/Conda | Node/npm | other]
```

**For Java/Maven**:
```bash
# Display dependency tree
mvn dependency:tree

# Find conflicts
mvn dependency:tree | grep "conflict\|WARNING\|omitted"
```

**For Python/pip or Conda**:
```bash
# Check compatibility
pip check
conda install --dry-run [package=version]
```

**For Node/npm**:
```bash
# Display conflicts
npm ls [package]
npm audit
```

### Step 2 — Conflict analysis

Identify:
1. **Who requires what**: which dependency/module requires the incompatible version
2. **Conflict graph**: A requires X@2.0, B requires X@1.8 — who is A, who is B
3. **Breaking changes**: check the library's CHANGELOG between the conflicting versions

**Sources to consult** (in order):
1. Official library CHANGELOG
2. Release notes for the target version
3. Library GitHub issues
4. Official migration guide

### Step 3 — Resolution strategies

**Strategy A: Coordinated update**
If both conflicting dependencies have versions compatible with a common version:
```xml
<!-- Maven — force the version in dependencyManagement -->
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>com.example</groupId>
      <artifactId>lib-x</artifactId>
      <version>2.0.0</version>
    </dependency>
  </dependencies>
</dependencyManagement>
```

**Strategy B: Exclusion + replacement**
If a transitive dependency causes conflicts:
```xml
<!-- Maven — exclude the problematic transitive dependency -->
<dependency>
  <groupId>com.example</groupId>
  <artifactId>lib-a</artifactId>
  <exclusions>
    <exclusion>
      <groupId>com.conflicting</groupId>
      <artifactId>lib-x</artifactId>
    </exclusion>
  </exclusions>
</dependency>
```

**Strategy C: Controlled downgrade**
If the target is not yet compatible, use the highest available compatible version.

**Strategy D: Shading/relocation**
Only if nothing else works — create a fat-jar with relocated dependencies (a heavyweight strategy, use with caution).

**Strategy E: Workaround for inconsistent behaviour**
If the library behaves differently from its documentation:
1. Isolate the behaviour in an adapter/wrapper
2. Document the workaround in the code with an explicit comment
3. Add a test that verifies the current behaviour

### Step 4 — Verification

After resolution:
1. Clean build without conflict warnings
2. Existing tests pass
3. The expected behaviour is restored
4. The solution is documented

---

## Critical dependencies of the current project

Before applying generic strategies, check whether the project has already documented known constraints (e.g. `docs/dependencies.md`, comments in `pom.xml` / `package.json` / `requirements.txt`, `CONTRIBUTING.md`). If documented compatibility notes exist, respect them.

If no documentation exists, **propose adding it** after resolving the conflict: an explicit comment in the dependency file is worth more than a wiki that nobody reads.

---

## Required output

1. **Diagnosis**: description of the identified conflict
2. **Chosen strategy**: which approach is applied and why
3. **Changes**: exact modifications to dependency files (pom.xml, environment.yml, package.json, requirements.txt, etc.)
4. **Verification commands**: how to test that the problem is resolved
5. **Documented workaround**: if a workaround was used, how it should be documented in the code

---

## Limits of this skill

- Does not replace the official documentation of libraries
- Cannot resolve breaking changes that require significant refactoring → hand off to `/refactoring/refactoring-expert`
- Does not test fixes autonomously — testing is always the developer's responsibility
- If the problem requires more than 2 hours of research, escalate to the team or open an issue on the library

---

$ARGUMENTS
