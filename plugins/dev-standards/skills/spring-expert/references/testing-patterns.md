# Testing patterns

## Testing with Spring

### Unit test — without Spring context (preferred for speed)

```java
@ExtendWith(MockitoExtension.class)
class CompanyServiceImplTest {

    @Mock CompanyRepository companyRepository;
    @Mock CompanyMapper companyMapper;
    @InjectMocks CompanyServiceImpl companyService;

    @Test
    void getById_existingCompany_returnsResponse() {
        Company company = Company.builder().id(1L).name("Acme").build();
        CompanyResponse expected = new CompanyResponse(1L, "Acme", null, null);

        when(companyRepository.findById(1L)).thenReturn(Optional.of(company));
        when(companyMapper.toResponse(company)).thenReturn(expected);

        assertThat(companyService.getById(1L)).isEqualTo(expected);
        verify(companyRepository).findById(1L);
    }

    @Test
    void getById_missing_throwsNotFoundException() {
        when(companyRepository.findById(99L)).thenReturn(Optional.empty());
        assertThatThrownBy(() -> companyService.getById(99L))
            .isInstanceOf(EntityNotFoundException.class);
    }
}
```

### Controller integration test with @WebMvcTest

```java
@WebMvcTest(CompanyController.class)
class CompanyControllerTest {

    @Autowired MockMvc mockMvc;
    @MockBean CompanyService companyService;
    @MockBean JwtService jwtService; // if Security is included

    @Test
    @WithMockUser(roles = "USER")
    void getCompany_validId_returns200() throws Exception {
        when(companyService.getById(1L))
            .thenReturn(new CompanyResponse(1L, "Acme", "12345678901", "EXT001"));

        mockMvc.perform(get("/api/companies/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("Acme"))
            .andExpect(jsonPath("$.vatNumber").value("12345678901"));
    }

    @Test
    void getCompany_unauthenticated_returns401() throws Exception {
        mockMvc.perform(get("/api/companies/1"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    @WithMockUser
    void createCompany_invalidRequest_returns400() throws Exception {
        String invalidBody = """
            {"name": "", "vatNumber": "INVALID", "email": "not-an-email"}
            """;

        mockMvc.perform(post("/api/companies")
                .contentType(MediaType.APPLICATION_JSON)
                .content(invalidBody))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.code").value("VALIDATION_ERROR"));
    }
}
```

### Integration test with a real H2 database

```java
@SpringBootTest
@ActiveProfiles("dev")
@Transactional // rollback after each test
class CompanyRepositoryIntegrationTest {

    @Autowired CompanyRepository companyRepository;

    @Test
    void findByExternalCode_existing_returnsCompany() {
        companyRepository.save(Company.builder()
            .name("Test Corp").externalCode("EXT-TEST").vatNumber("12345678901").build());

        assertThat(companyRepository.findByExternalCode("EXT-TEST"))
            .isPresent()
            .get().extracting(Company::getName).isEqualTo("Test Corp");
    }
}
```

---
