# Code formatting (non-negotiable)

Annotation stacking, POM layout and the ban on inline response construction,
with the correct and incorrect form of each.

## Contents

- [Annotation formatting: one per line, vertically stacked](#annotation-formatting-one-per-line-vertically-stacked)
- [POM file formatting](#pom-file-formatting)
- [Inline response construction: forbidden](#inline-response-construction-forbidden)

## Annotation formatting: one per line, vertically stacked

Each annotation goes on its own line. Never inline-stack annotations on a single line, neither on classes, methods, fields, nor parameters. Logical groups of field annotations may be separated by a blank line.

```java
// ❌ WRONG — annotations inlined
@Entity @Table(name = "companies") public class Company { ... }

@NotNull @Size(max = 50) private String name;

// ✅ CORRECT — one annotation per line
@Entity
@Table(name = "companies")
public class Company { ... }

@NotNull
@Size(max = 50)
private String name;
```

For records, the same rule applies to component declarations:

```java
public record CompanyCreateRequest(
    @NotBlank
    @Size(max = 200)
    String name,

    @NotBlank
    @Pattern(regexp = "^[0-9]{11}$")
    String vatNumber,

    @Email
    String email
) {}
```

## POM file formatting

`pom.xml` is XML: it must be hierarchically indented, one element per line, never collapsed. Use 4-space indentation (Maven default). Generated POMs that are written as a single line or with all `<dependency>` blocks on one line each are rejected.

```xml
<!-- ✅ CORRECT -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>

<!-- ❌ WRONG -->
<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
```

## Inline response construction: forbidden

Controllers and services must never return `Map.of(...)`, `HashMap<>`, or anonymous inline classes as response bodies. Always return a typed DTO produced by a `*Mapper` class. See `spring-architecture` for the full mapper-layer rules.

---
