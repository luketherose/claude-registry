# Report

`GET /api/reports/daily` returns HTTP 500 for roughly one call in twenty.
Retrying the same URL usually succeeds. Load is 40 requests/second.

## Access log excerpt

```
09:31:04 GET /api/reports/daily 200 118ms
09:31:04 GET /api/reports/daily 200 121ms
09:31:05 GET /api/reports/daily 500 30012ms
09:31:05 GET /api/reports/daily 200 130ms
09:31:07 GET /api/reports/daily 500 30008ms
```

## Error

```
org.springframework.jdbc.CannotGetJdbcConnectionException: Failed to obtain JDBC Connection
Caused by: java.sql.SQLTransientConnectionException: HikariPool-1 - Connection is not available, request timed out after 30000ms
	at com.example.report.ReportService.buildDaily(ReportService.java:52)
```

## ReportService.java (extract)

```java
@Transactional(readOnly = true)
public DailyReport buildDaily(LocalDate day) {
    Connection extra = dataSource.getConnection();
    List<Row> rows = jdbcTemplate.query(DAILY_SQL, day);
    return aggregate(rows, extra);
}
```

## application.yml (extract)

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10
      connection-timeout: 30000
```
