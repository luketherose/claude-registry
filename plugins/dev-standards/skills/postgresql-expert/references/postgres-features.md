# Postgres features

## Contents

- 3. PostgreSQL Best Practices
- Data types — choose with precision
- Indices — types and when to use them
- EXPLAIN ANALYZE — practical reading
- Transactions — correct usage
- Locking and concurrency

## 3. PostgreSQL Best Practices

### Data types — choose with precision

```sql
-- Text
name TEXT                       -- preferable to VARCHAR(n) for flexibility
code CHAR(12)                   -- known fixed length → CHAR
email TEXT                      -- not VARCHAR(255) — the 255 is a MySQL legacy

-- Numbers
nominal_value NUMERIC(15, 2)    -- monetary values → NUMERIC, never FLOAT (rounding errors)
rate NUMERIC(5, 4)              -- percentage with 4 decimal places
quantity INTEGER                -- integer counters

-- Dates and times
created_at TIMESTAMPTZ          -- TIMESTAMPTZ (with time zone) for absolute timestamps
report_date DATE                -- DATE for dates without time
duration INTERVAL               -- duration → INTERVAL, not INTEGER days

-- Booleans
is_active BOOLEAN NOT NULL DEFAULT true   -- never SMALLINT(1) as a surrogate

-- Identifiers
id BIGINT GENERATED ALWAYS AS IDENTITY
external_id UUID DEFAULT gen_random_uuid()

-- Semi-structured JSON
metadata JSONB                  -- JSONB (binary, indexable) not JSON (text, slow)
```

**JSONB — when to use and when not to**:

```sql
-- ✅ Use JSONB for semi-structured data that varies per record and does not require frequent queries
ALTER TABLE companies ADD COLUMN extra_data JSONB;
-- Query: company.extra_data->>'sector' — slow without an index

-- ✅ With GIN index for key/value queries
CREATE INDEX idx_companies_extra_data ON companies USING GIN (extra_data);
-- Now: SELECT * FROM companies WHERE extra_data @> '{"sector": "Finance"}' is fast

-- ❌ Do not use JSONB as a substitute for structured relations
-- If you query extra_data->>'city' frequently, that column should be a real column
```

### Indices — types and when to use them

```sql
-- B-tree (default) — for =, <, >, BETWEEN, ORDER BY, LIKE 'prefix%'
CREATE INDEX idx_companies_name ON companies (name);
CREATE INDEX idx_items_expiry ON items (expiry_date);

-- Composite — most selective column FIRST, then columns for ORDER BY or range
CREATE INDEX idx_items_owner_status ON items (owner_id, status);
-- Supports: WHERE owner_id = 1 AND status = 'ACTIVE'
-- Also supports: WHERE owner_id = 1 alone
-- Does NOT support: WHERE status = 'ACTIVE' alone (leading column missing)

-- Partial index — only for a data subset (reduces index size)
CREATE INDEX idx_items_active ON items (owner_id, expiry_date)
    WHERE status = 'ACTIVE';
-- Used only for queries with WHERE status = 'ACTIVE' — very efficient

-- GIN — for JSONB, arrays, full-text search
CREATE INDEX idx_companies_extra_gin ON companies USING GIN (extra_data);
CREATE INDEX idx_companies_name_fts ON companies
    USING GIN (to_tsvector('english', name));

-- GiST — for range types, geometry
CREATE INDEX idx_events_during ON events USING GiST (during);

-- Expression index — for queries on functions
CREATE INDEX idx_companies_name_lower ON companies (LOWER(name));
-- Supports: WHERE LOWER(name) = 'acme'
```

**Rule**: an index on an FK is almost always necessary for JOIN queries and for `ON DELETE` operations (PostgreSQL does not create it automatically the way MySQL does).

```sql
-- FK without index → full scan on the child table on every DELETE on the parent
CREATE INDEX idx_items_owner_id ON items (owner_id);
CREATE INDEX idx_contacts_company_id ON contacts (company_id);
```

### EXPLAIN ANALYZE — practical reading

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT c.name, COUNT(i.id) as item_count
FROM companies c
LEFT JOIN items i ON i.owner_id = c.id AND i.status = 'ACTIVE'
WHERE c.status = 'ACTIVE'
GROUP BY c.id, c.name
ORDER BY item_count DESC;
```

**What to look for**:
- `Seq Scan` on a large table → consider an index
- `Nested Loop` with many rows → evaluate `Hash Join` (increase `work_mem`)
- `cost=X..Y` — planner estimate; `actual time=X..Y` — real time
- `rows=N` vs `actual rows=M` — if very different, stale statistics → `ANALYZE table`
- `Buffers: hit=N read=M` — high `read` → data not in cache → I/O problem

```sql
-- Stale statistics — refresh them
ANALYZE companies;

-- Set memory for complex queries (current session only)
SET work_mem = '64MB';
EXPLAIN ANALYZE <query>;
RESET work_mem;
```

### Transactions — correct usage

```sql
-- Explicit transaction
BEGIN;
    UPDATE companies SET status = 'INACTIVE' WHERE id = 42;
    INSERT INTO audit_log (entity, entity_id, action, changed_at)
        VALUES ('Company', 42, 'DEACTIVATE', NOW());
COMMIT;
-- On error: automatic ROLLBACK

-- Savepoint — for partial rollback
BEGIN;
    INSERT INTO items (...) VALUES (...);
    SAVEPOINT sp1;
    INSERT INTO item_allocations (...) VALUES (...);
    -- If allocation fails: roll back to savepoint, keep the item insert
    ROLLBACK TO SAVEPOINT sp1;
COMMIT;
```

### Locking and concurrency

```sql
-- SELECT FOR UPDATE — row lock for update (prevents lost update)
BEGIN;
SELECT * FROM items WHERE id = 1 FOR UPDATE;
-- No other session can modify this row until COMMIT
UPDATE items SET status = 'PROCESSING' WHERE id = 1;
COMMIT;

-- SELECT FOR UPDATE SKIP LOCKED — for job queues / task processing
SELECT * FROM processing_queue
WHERE status = 'PENDING'
ORDER BY created_at
LIMIT 10
FOR UPDATE SKIP LOCKED; -- skip rows already locked by other workers

-- Advisory lock — for application-level operations
SELECT pg_try_advisory_xact_lock(12345); -- false if already locked → non-blocking
```

**Isolation levels** — PostgreSQL default is `READ COMMITTED`. For critical financial operations:

```sql
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- Reads always see the same snapshot — protects against non-repeatable reads
COMMIT;
```

---
