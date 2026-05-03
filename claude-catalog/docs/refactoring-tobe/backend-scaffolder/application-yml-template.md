# application.yml template

> Reference doc for `backend-scaffolder`. Read at runtime when generating
> `src/main/resources/application.yml` (Method step 8).

## Template

```yaml
spring:
  application:
    name: <app-name>
  datasource:
    url: ${DB_URL:jdbc:postgresql://localhost:5432/<db>}
    username: ${DB_USER:<app>}
    password: ${DB_PASSWORD:}
  jpa:
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        jdbc:
          time_zone: UTC
    open-in-view: false
  liquibase:
    enabled: true
    change-log: classpath:db/changelog/db.changelog-master.yaml
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: ${OAUTH2_ISSUER_URI:http://localhost:8080/realms/<app>}

server:
  port: 8080
  forward-headers-strategy: framework

management:
  endpoints:
    web:
      exposure:
        include: [health, info, prometheus]
  metrics:
    export:
      prometheus:
        enabled: true
```

`hardening-architect` adds tracing / logging-format on top of this.
