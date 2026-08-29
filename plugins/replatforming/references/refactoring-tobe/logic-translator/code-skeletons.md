# Logic-translator — code skeletons

> Reference doc for `logic-translator`. Read at runtime when translating
> the AS-IS Python implementation of a UC into Java service / domain code.
> The agent body keeps the **decision logic** (which mode, when to introduce
> a state-machine method, when to defer to ADR); this doc holds the
> **code skeletons** the agent fills in.

The three skeletons map 1:1 to the `code scope` modes the supervisor
passes in: `full`, `scaffold-todo` (DEFAULT), `structural`. Pick the
matching skeleton, then fill it with the AS-IS-derived names, fields,
and references. A fourth skeleton — state-machine method on a domain
entity — applies in any mode when the UC involves a state transition.

---

## `full` mode — complete service implementation

Produce a complete service implementation:

```java
@Service
@Transactional
public class UserService {

    private final UserRepository userRepository;
    private final IdempotencyService idempotency;
    private final PasswordHasher passwordHasher;
    private final UserMapper mapper;

    public UserService(UserRepository userRepository,
                       IdempotencyService idempotency,
                       PasswordHasher passwordHasher,
                       UserMapper mapper) {
        this.userRepository = userRepository;
        this.idempotency = idempotency;
        this.passwordHasher = passwordHasher;
        this.mapper = mapper;
    }

    /**
     * UC-01 — Register a new user.
     *
     * AS-IS source ref:
     *   <repo>/infosync/auth/register.py:48 (def register_user)
     *
     * Translation notes:
     *   - email uniqueness: AS-IS checks via SELECT then INSERT
     *     (race condition risk per Phase 2 RISK-DA-04). TO-BE relies
     *     on UNIQUE constraint on users.email + catches
     *     DataIntegrityViolationException → throws
     *     ValidationException("email already registered").
     *   - password hashing: AS-IS uses werkzeug; TO-BE uses
     *     BCryptPasswordEncoder (Spring Security default).
     *   - email verification: out of this UC's scope; UC-04
     *     handles confirmation.
     */
    public UserDto registerUser(String idempotencyKey, CreateUserRequest request) {
        // Idempotency check
        var existing = idempotency.lookup(idempotencyKey, "registerUser", request);
        if (existing.isPresent()) {
            return existing.get();
        }

        // Validation (additional rules beyond bean validation)
        if (request.password().length() < 8) {
            throw new ValidationException("password too short");
        }

        // Persist
        var user = User.register(
            request.email(),
            passwordHasher.hash(request.password()),
            request.fullName());
        try {
            user = userRepository.save(user);
        } catch (DataIntegrityViolationException e) {
            throw new ValidationException("email already registered");
        }

        // Map and snapshot for idempotency
        var dto = mapper.toDto(user);
        idempotency.snapshot(idempotencyKey, "registerUser", request, dto);
        return dto;
    }
}
```

---

## `scaffold-todo` mode (DEFAULT) — happy path + TODO markers

Happy path implementation + explicit TODO markers for complex branches:

```java
public UserDto registerUser(String idempotencyKey, CreateUserRequest request) {
    // Idempotency
    // TODO(BC-01, UC-01): wire IdempotencyService once shared/idempotency
    //   is finalized (currently scaffold). For now: skip lookup.
    //   AS-IS source ref: <repo>/infosync/auth/register.py:48

    // Happy path: create user
    var user = User.register(
        request.email(),
        // TODO(BC-01, UC-01): integrate Spring Security BCryptPasswordEncoder
        //   for password hashing. AS-IS uses werkzeug.
        request.password(),
        request.fullName());
    user = userRepository.save(user);

    // TODO(BC-01, UC-01): catch DataIntegrityViolationException for
    //   duplicate email and translate to ValidationException
    //   (AS-IS RISK-DA-04: race-condition window between SELECT and INSERT)

    return mapper.toDto(user);
}
```

The happy path runs (compiles, returns a result) but the TODOs flag
where production-grade behavior is still missing. Phase 5 tests will
xfail for these incomplete UCs — the same xfail pattern as Phase 3
AS-IS bugs.

---

## `structural` mode — method signatures only

```java
public UserDto registerUser(String idempotencyKey, CreateUserRequest request) {
    // TODO(BC-01, UC-01): translate from <as-is-source-ref>
    throw new UnsupportedOperationException("UC-01 not yet implemented");
}
```

This is the same as the scaffolder left it; in `structural` mode you
just confirm the signature and AS-IS ref. Useful when the user wants
Phase 4 as a "preparation" stage.

---

## State-machine method on a domain entity

If the UC involves state transitions on an entity (per Phase 1
implicit logic), translate the state machine into a method on the
entity:

```java
// Inside User.java
/**
 * Activate a user (typically after email confirmation).
 *
 * Allowed only from PENDING status. Throws InvalidStateTransition
 * otherwise.
 *
 * AS-IS source ref: <repo>/infosync/auth/activate.py:22
 */
public void activate() {
    if (this.status != UserStatus.PENDING) {
        throw new InvalidStateTransition(
            "cannot activate user in status " + this.status);
    }
    this.status = UserStatus.ACTIVE;
    this.updatedAt = Instant.now();
}
```

The service then calls `user.activate()` rather than mutating the field
directly. This preserves invariants.
