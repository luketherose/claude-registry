# Maven POM template

> Reference doc for `backend-scaffolder`. Read at runtime when generating
> `<backend-dir>/pom.xml` (Method step 1 — Project skeleton).

## Goal

Produce a `pom.xml` honoring ADR-002 (target stack). Spring Boot 3, Java
version per ADR-002, build with `mvn compile` after `data-mapper` runs.

## Coordinates

- `groupId` / `artifactId` / `version` derived from project name (read from
  `.indexing-kb/01-overview.md` if available, else placeholder with TODO).
- Spring Boot version from ADR-002.
- Java version from ADR-002 (default 21 if unspecified).

## Core dependencies

- `spring-boot-starter-web` (or `webflux` only if ADR-001 specified)
- `spring-boot-starter-data-jpa`
- `spring-boot-starter-security`
- `spring-boot-starter-validation`
- `spring-boot-starter-actuator`
- `org.liquibase:liquibase-core` (Flyway is forbidden in TO-BE projects)
- `com.h2database:h2` (test/local profile)
- `org.postgresql:postgresql` (or whichever DB ADR-002 dictates)
- `org.springdoc:springdoc-openapi-starter-webmvc-ui` (serves OpenAPI spec
  at runtime)
- `io.micrometer:micrometer-registry-prometheus`

## Test dependencies

- `spring-boot-starter-test`
- `org.testcontainers:postgresql` (or matching DB)
- `org.testcontainers:junit-jupiter`

## Plugins

- `spring-boot-maven-plugin`
- `org.openapitools:openapi-generator-maven-plugin` configured to read
  `../docs/refactoring/4.6-api/openapi.yaml` and generate API interfaces —
  the controller `implements` these. No client generation for BE.
