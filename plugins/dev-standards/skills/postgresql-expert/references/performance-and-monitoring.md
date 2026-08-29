# Performance and monitoring

## Contents

- 4. Performance and Optimisation
- Efficient pagination
- Batch operations
- Query anti-patterns
- Statistics and autovacuum
- 7. Logging, Monitoring and Debugging
- Slow queries — configuration
- pg_stat_statements — aggregate query analysis
- Key metrics to monitor

## 4. Performance and Optimisation

### Efficient pagination

```sql
-- ❌ OFFSET on large tables — PostgreSQL reads and discards all preceding records
SELECT * FROM companies ORDER BY id LIMIT 20 OFFSET 10000; -- slow with high N

-- ✅ Keyset pagination (cursor-based) — O(log N) with index on id
SELECT * FROM companies
WHERE id > :lastSeenId  -- lastSeenId from the previous page
ORDER BY id
LIMIT 20;

-- For multi-column ordering
SELECT * FROM companies
WHERE (name, id) > (:lastName, :lastId) -- tuple comparison
ORDER BY name, id
LIMIT 20;
```

**Keyset vs OFFSET**: keyset is stable (no row skipping on concurrent inserts) and scalable. OFFSET is only usable for early pages (< 100) or when the user jumps to arbitrary pages (search engine style).

### Batch operations

```sql
-- ❌ N single INSERTs (called from a Java loop)
INSERT INTO items (...) VALUES (...);
INSERT INTO items (...) VALUES (...); -- N times

-- ✅ Multi-row INSERT
INSERT INTO items (code, owner_id, nominal_value, expiry_date)
VALUES
    ('CODE0001', 1, 5000000.00, '2028-12-31'),
    ('CODE0002', 1, 3000000.00, '2027-06-30'),
    ('CODE0003', 2, 8000000.00, '2029-03-31');

-- ✅ COPY for bulk load (orders of magnitude faster than INSERT)
COPY companies (name, vat_number, business_code) FROM '/tmp/companies.csv' CSV HEADER;
```

### Query anti-patterns

```sql
-- ❌ Function on an indexed column in WHERE — the index is not used
SELECT * FROM companies WHERE UPPER(name) = 'ACME';
-- ✅ Functional index or normalise the data
CREATE INDEX idx_companies_name_upper ON companies (UPPER(name));

-- ❌ LIKE with leading wildcard — does not use B-tree
SELECT * FROM companies WHERE name LIKE '%acme%';
-- ✅ Full-text search for substring matching
SELECT * FROM companies WHERE to_tsvector('english', name) @@ to_tsquery('acme');

-- ❌ NOT IN with subquery — behaves poorly with NULLs
SELECT * FROM companies WHERE id NOT IN (SELECT owner_id FROM items);
-- ✅ NOT EXISTS or LEFT JOIN / IS NULL
SELECT c.* FROM companies c
LEFT JOIN items i ON i.owner_id = c.id
WHERE i.id IS NULL;

-- ❌ SELECT * in production — loads unnecessary columns, invalidates cache
SELECT * FROM companies JOIN contacts ON ...;
-- ✅ Select only required columns
SELECT c.id, c.name, c.business_code FROM companies c JOIN ...;

-- ❌ Implicit conversion — invalidates indices
SELECT * FROM companies WHERE id = '42'; -- id is BIGINT, '42' is TEXT
-- ✅ Consistent types
SELECT * FROM companies WHERE id = 42;
```

### Statistics and autovacuum

```sql
-- Tables with frequent updates/deletes accumulate dead tuples → performance degradation
-- VACUUM removes them; AUTOVACUUM does this automatically, but may need tuning

-- Check dead tuples
SELECT relname, n_dead_tup, n_live_tup,
       round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 2) AS dead_pct
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- Force manual vacuum/analyse if necessary
VACUUM ANALYZE companies;
```

---

## 7. Logging, Monitoring and Debugging

### Slow queries — configuration

```sql
-- postgresql.conf (or ALTER SYSTEM for runtime changes)
log_min_duration_statement = 1000   -- log queries > 1 second (production)
log_min_duration_statement = 100    -- 100ms in staging
log_min_duration_statement = 0      -- all queries in dev (verbose)

log_statement = 'none'              -- do not log everything — use min_duration
log_lock_waits = on                 -- log waits on locks > deadlock_timeout
deadlock_timeout = 1s

-- Apply at runtime without restart
ALTER SYSTEM SET log_min_duration_statement = '1000';
SELECT pg_reload_conf();
```

### pg_stat_statements — aggregate query analysis

```sql
-- Enable the extension (requires superuser or pg_monitor)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Slowest queries by total time
SELECT query,
       calls,
       round(total_exec_time::numeric, 2) AS total_ms,
       round(mean_exec_time::numeric, 2) AS avg_ms,
       round(stddev_exec_time::numeric, 2) AS stddev_ms,
       rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- Queries with high variance — candidates for optimisation
SELECT query, calls,
       round(mean_exec_time::numeric, 2) AS avg_ms,
       round(stddev_exec_time::numeric, 2) AS stddev_ms
FROM pg_stat_statements
WHERE calls > 100
ORDER BY stddev_exec_time DESC
LIMIT 10;
```

### Key metrics to monitor

```sql
-- Active and idle connections
SELECT state, count(*)
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state;

-- Waiting locks — signal of contention
SELECT pid, query, wait_event_type, wait_event, state
FROM pg_stat_activity
WHERE wait_event IS NOT NULL
  AND datname = current_database();

-- Table and index sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname || '.' || tablename)) AS table_size,
    pg_size_pretty(pg_indexes_size(schemaname || '.' || tablename)) AS index_size
FROM pg_tables
WHERE schemaname = 'schema_main'
ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC;

-- Unused indices — candidates for removal
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname = 'schema_main'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Cache hit ratio — should be > 99% in production
SELECT
    round(blks_hit::numeric / NULLIF(blks_hit + blks_read, 0) * 100, 2) AS cache_hit_pct
FROM pg_stat_database
WHERE datname = current_database();
```

---
