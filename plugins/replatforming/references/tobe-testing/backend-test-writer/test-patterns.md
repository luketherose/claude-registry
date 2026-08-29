# Backend test patterns

> Reference doc for `backend-test-writer`. Read at runtime when authoring
> the JUnit 5 + Mockito + Testcontainers + Spring Cloud Contract suite.
> Decision logic (coverage policy, constraints, bug carry-over) stays in
> the agent body — this doc only carries the verbatim test-class
> skeletons and Groovy DSL templates.

## Goal

Provide copy-and-adapt templates for the four canonical test layers
authored by `backend-test-writer`:

1. Unit test (service) — JUnit 5 + Mockito, no Spring context.
2. Integration test (full Spring + Testcontainers).
3. Contract test (Spring Cloud Contract producer DSL).
4. Error contract test (RFC 7807 ProblemDetail).

Cover happy path, each branch, each exception, and each invariant per
class under test.

---

## Unit test (service)

```java
@ExtendWith(MockitoExtension.class)
class <Service>Test {

    @Mock private <Repository> repository;
    @Mock private <Mapper> mapper;
    @InjectMocks private <Service> service;

    @Test
    void <method>_happyPath_returnsExpected() {
        // given
        var input = ...;
        var domain = ...;
        when(repository.findById(...)).thenReturn(Optional.of(domain));
        when(mapper.toDto(domain)).thenReturn(...);

        // when
        var result = service.<method>(input);

        // then
        assertThat(result).isEqualTo(...);
        verify(repository).save(domain);
    }

    @Test
    void <method>_invalidInput_throwsValidation() { /* ... */ }

    @Test
    void <method>_aggregateNotFound_throwsNotFound() { /* ... */ }
}
```

Cover: happy path + each branch + each exception + each invariant.

---

## Integration test (full Spring context with Testcontainers)

```java
@SpringBootTest
@Testcontainers
@AutoConfigureMockMvc
class <UC-id>IntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16-alpine");

    @DynamicPropertySource
    static void registerProps(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired private MockMvc mockMvc;

    @Test
    void <ucId>_happyPath() throws Exception {
        mockMvc.perform(
                post("/v1/<resource>")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(loadFixture("happy-path-input.json")))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").exists())
            .andExpect(jsonPath("$.<field>").value("<expected>"));
    }
}
```

---

## Contract test (Spring Cloud Contract producer)

For each `operationId` in OpenAPI, produce a Groovy DSL contract:

```groovy
// backend/src/test/resources/contracts/<bc>/<operationId>.groovy
Contract.make {
    description "POST /v1/<resource> creates <Aggregate>"
    request {
        method 'POST'
        url '/v1/<resource>'
        headers { contentType('application/json'); header('Idempotency-Key', anyUuid()) }
        body([
            name: $(consumer(anyNonEmptyString()), producer("Test"))
        ])
    }
    response {
        status 201
        headers { contentType('application/json') }
        body([
            id: $(consumer(anyUuid()), producer("11111111-1111-1111-1111-111111111111")),
            name: "Test"
        ])
    }
}
```

Maven plugin `spring-cloud-contract-maven-plugin` generates the
JUnit verifier tests from the contracts. Provide a base class
`<BC>ContractVerifierBase.java` that boots a minimal Spring context.

---

## Error contract test (RFC 7807 ProblemDetail)

For every documented error response in OpenAPI, write a contract that
verifies the ProblemDetail shape:

```groovy
Contract.make {
    description "POST /v1/<resource> with invalid input returns 400 ProblemDetail"
    request {
        method 'POST'
        url '/v1/<resource>'
        headers { contentType('application/json') }
        body([ name: '' ])
    }
    response {
        status 400
        headers { contentType('application/problem+json') }
        body([
            type: 'https://example.com/errors/validation',
            title: 'Validation failed',
            status: 400,
            detail: anyNonEmptyString(),
            instance: anyNonEmptyString()
        ])
    }
}
```
