---
name: python-to-java-migration-expert
description: "This skill should be used when translating a Python application to Java on Spring Boot: mapping Python concepts to Java idioms, finding library equivalences (Django ORM to JPA, Celery to Spring Batch or @Async, decorators to Spring AOP), planning data migration, and avoiding known translation pitfalls. Use it after the target architecture is defined, to produce module-by-module migration specifications. Do not use it for frontend migration (use python-to-angular-migration-expert or python-to-react-migration-expert) or before the target component structure is known."
---
# Python to Java Migration Expert

Migrate Django, Flask, FastAPI and Celery-based systems to Spring Boot microservices at the specification level. Work from the idiomatic differences between the two ecosystems: how Python's dynamic typing translates to Java generics and type safety, how Django ORM maps to JPA/Hibernate, how Celery tasks become Spring Batch or @Async methods, how Python decorators map to Spring AOP and annotations. Produce migration specifications that Java developers can implement without Python knowledge.

## Key Concept Mappings (Built-in Reference)

These mappings are always valid regardless of the specific scope:

| Python Concept | Java/Spring Equivalent | Notes |
|---|---|---|
| `class` (data) | `record` / `@Entity` / `@Value` | Records for immutable DTOs, Entity for DB |
| `@dataclass` | `record` / Lombok `@Data` | |
| `dict` | `Map<K,V>` | `HashMap`, `LinkedHashMap` |
| `list` | `List<T>` | `ArrayList`, `LinkedList` |
| `Optional[T]` | `Optional<T>` | Java Optional, different semantics |
| `async/await` | `CompletableFuture` / WebFlux | Choose based on architecture |
| `@decorator` | `@Aspect` (AOP) or `@Annotation` | |
| `__init__` | Constructor / `@PostConstruct` | |
| `__str__` | `toString()` | |
| Django ORM `.filter()` | JPA `findBy*` / `@Query` JPQL | |
| Django `models.Model` | `@Entity` JPA class | |
| Flask/FastAPI route | Spring `@RestController` + `@RequestMapping` | |
| Celery task | Spring `@Async` / Spring Batch Step | |
| Django signals | Spring Events (`ApplicationEventPublisher`) | |
| Python exceptions | Java checked/unchecked exceptions | Design decision needed |
| `**kwargs` | Builder pattern / `Map<String, Object>` | |
| Duck typing | Interface / Generic type bound | Requires explicit interface design |
| `property` | Getter/setter / Lombok | |
| Context manager (`with`) | `try-with-resources` | |
| `requirements.txt` | `pom.xml` / `build.gradle` | Maven or Gradle |
| `.env` / `os.environ` | `application.properties` / Vault | Spring profiles |

---

## Constraints
- Java-idiomatic code only (not transliterated Python)
- Stubs only, no complete implementations
- [ARCHITECTURAL DECISION NEEDED:] for patterns with no direct equivalent
- Every BR-N must have implementation guidance
- Pitfall register must cover ≥ 5 items

---

## Quality Checklist

- [ ] All Python libraries mapped to Java equivalents
- [ ] All business rules have Java implementation guidance
- [ ] All Java stubs use correct Spring annotations
- [ ] Pitfall register has ≥ 5 items
- [ ] [ARCHITECTURAL DECISION NEEDED:] used for unresolved patterns

---

## Detailed references

- **Full output specification, section by section**: see [references/output-specification.md](references/output-specification.md)
- **A worked example: input and expected output excerpt**: see [references/worked-example.md](references/worked-example.md)
