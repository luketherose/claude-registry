# Business-logic analyst — detection patterns

> Reference doc for `business-logic-analyst`. Read at runtime when starting
> domain-concept extraction or the validation-rules pass — provides the
> per-language type-definition markers and validation grep patterns.

The agent body owns the decision logic (which pass runs when, what to skip,
when to stop). This doc is the language-aware lookup only.

---

## Type definitions per language

For each domain concept, look for its definition using these markers.

| Language | Type-definition keywords |
|---|---|
| python | `class`, `@dataclass`, Pydantic `BaseModel`, `TypedDict`, `NamedTuple` |
| java | `class`, `record` (Java 14+), `interface`, `enum` |
| kotlin | `data class`, `class`, `sealed class` / `sealed interface`, `enum class`, `object`, value class (`@JvmInline`) |
| go | `type X struct { ... }`, `type X interface { ... }`, `type X = ...` (alias) |
| rust | `struct`, `enum`, `trait`, `type` alias |
| csharp | `class`, `record`, `record struct`, `interface`, `enum`, `struct` |
| ruby | `class`, `module`, `Struct.new(...)` |
| php | `class`, `interface`, `trait`, `enum` (PHP 8.1+), `readonly class` (PHP 8.2+) |
| typescript | `class`, `interface`, `type` alias, `enum`, discriminated unions |

For each domain concept, capture: where it is defined, its key
attributes / fields and their types, and the sites where it is constructed
or transformed.

Skip generic infrastructure terms: `Logger`, `Config`, `Session`, `Client`,
`Manager`, `Service`, `Helper`, `Repository` (when used as a DI artifact
rather than a domain concept), `Controller`, `Handler`.

---

## Validation rule patterns

Read `02-structure/stack.json` to know which patterns to grep. For each
finding record: condition, error message, file:line, language.

| Language / framework | Validation patterns |
|---|---|
| python (pydantic) | `@validator`, `@field_validator`, `@model_validator`; `Field(gt=...)`, `Field(min_length=...)`; `BaseModel` constraints |
| python (general) | `assert <cond>` (in production code); `raise ValueError(`, `raise ValidationError(`, `raise <CustomError>(`; `if not <cond>: raise ...` |
| java/kotlin (bean-validation) | `@NotNull`, `@NotBlank`, `@Size`, `@Min`, `@Max`, `@Pattern`, `@Email`, custom `@interface` constraints; `@Valid` propagation |
| java (manual) | `Objects.requireNonNull(...)`, `Preconditions.check*` (Guava); `throw new IllegalArgumentException(...)` |
| kotlin | `require(<cond>) { ... }`, `requireNotNull(...)`, `check(<cond>) { ... }` |
| go | `if <cond> { return ..., fmt.Errorf("...") }`; `validator.Validate(...)`; `go-playground/validator` struct tags |
| rust | `validator` crate `#[validate(...)]` derive; `assert!`, `debug_assert!`, `Result::Err(...)` paths |
| csharp | DataAnnotations (`[Required]`, `[StringLength]`, `[Range]`, `[RegularExpression]`); FluentValidation `RuleFor(...).NotEmpty().MaximumLength(...)` |
| ruby (rails) | `validates :field, presence: true, length: { maximum: ... }`; `validate :custom_method`; `before_validation` |
| ruby (general) | `raise ArgumentError, "..."` |
| php (laravel) | FormRequest `rules()` array; `$request->validate([...])` |
| php (symfony) | `#[Assert\NotBlank]`, `#[Assert\Length(min: ...)]` attributes |
| typescript / javascript | `class-validator` decorators (`@IsString`, `@MinLength`); zod `z.string().min(...)`; yup `string().required().min(...)`; manual `if (!cond) throw new Error(...)` |
| swift | `guard <cond> else { throw ... }` |

---

## Business-rule and state-machine markers

Look for conditional branches with **business** semantics (not technical):

- `if customer.tier == "premium":` — tier-based logic
- `if amount > <number>:` — threshold logic (especially with magic numbers)
- `if order.status in {"PENDING", "DRAFT"}:` — state-based behaviour
- Switch-like patterns: `if/elif` chains on enum or string values

Look for hardcoded constants used in conditions: thresholds (e.g.,
`MAX_AMOUNT = 10_000`), tier names (`PREMIUM`, `STANDARD`), status enums
(`OrderStatus.PENDING`).

State machines: functions that branch on a `.status` or `.state` field and
may transition it; enum classes whose values look like states.

Workflow function names (likely orchestrators): `process_*`, `handle_*`,
`execute_*`, `run_*`, `apply_*`, `compute_*`. For each, read the body
top-level only and describe in 3–5 bullets what happens, plus inputs and
outputs.
