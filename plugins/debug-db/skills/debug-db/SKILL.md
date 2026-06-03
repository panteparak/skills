---
name: debug-db
description: Debug database issues including slow queries, deadlocks, migration failures, and data integrity problems. Use when troubleshooting database-related issues.
argument-hint: "[database-issue-description]"
---

# Database Debugging

Investigate: **$ARGUMENTS**

## Diagnostic Process

### Step 1: Identify the Issue Type
- **Slow queries** → Query analysis
- **Deadlocks** → Lock analysis
- **Migration failures** → Migration debugging
- **Data integrity** → Constraint analysis
- **Connection issues** → Pool/connection debugging

## Slow Query Debugging (PostgreSQL)

```sql
-- 1. Find slow queries (pg_stat_statements)
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- 2. Analyze specific query
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) <your query>;

-- 3. Check for sequential scans on large tables
SELECT relname, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC;

-- 4. Check missing indexes
SELECT schemaname, tablename, attname, null_frac, n_distinct, correlation
FROM pg_stats
WHERE tablename = '<table>';

-- 5. Check table bloat
SELECT schemaname, tablename, n_live_tup, n_dead_tup,
       round(n_dead_tup::numeric / GREATEST(n_live_tup, 1) * 100, 2) as dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

### EXPLAIN Output Interpretation
| Node | Meaning | Fix |
|------|---------|-----|
| `Seq Scan` | Full table scan | Add index on filter columns |
| `Nested Loop` with high rows | N+1 join | Use `Hash Join` via proper indexing |
| `Sort` with high cost | In-memory/disk sort | Add index matching ORDER BY |
| `Hash Join` excessive | Large hash table | Check join conditions, add indexes |

## Deadlock Debugging

```sql
-- Check current locks
SELECT pid, locktype, relation::regclass, mode, granted, query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE NOT granted;

-- Check blocking queries
SELECT blocked.pid AS blocked_pid,
       blocked.query AS blocked_query,
       blocking.pid AS blocking_pid,
       blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks bl ON blocked.pid = bl.pid AND NOT bl.granted
JOIN pg_locks kl ON bl.locktype = kl.locktype AND bl.relation = kl.relation AND kl.granted
JOIN pg_stat_activity blocking ON kl.pid = blocking.pid;

-- Kill blocking query (last resort)
SELECT pg_terminate_backend(<pid>);
```

### Deadlock Prevention Patterns
- Always acquire locks in consistent order
- Keep transactions short
- Use `SELECT ... FOR UPDATE SKIP LOCKED` for queue-like patterns
- Use optimistic locking (version column) instead of pessimistic locking

## Migration Debugging

```bash
# Check migration status
# Flyway
flyway info
# Django
python manage.py showmigrations
# Goose
goose status

# Common migration failures:
# 1. Column already exists → Migration not idempotent
# Fix: Use IF NOT EXISTS / IF EXISTS
ALTER TABLE t ADD COLUMN IF NOT EXISTS col TEXT;

# 2. Data migration timeout → Large table lock
# Fix: Run in batches, use concurrent index creation
CREATE INDEX CONCURRENTLY idx_name ON table(col);

# 3. Foreign key violation → Data doesn't satisfy constraint
# Fix: Clean data first, then add constraint
```

## Connection Pool Debugging

```sql
-- Check connection count
SELECT count(*) FROM pg_stat_activity;
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;

-- Check max connections
SHOW max_connections;

-- Find long-running idle connections
SELECT pid, state, query, state_change, now() - state_change AS idle_time
FROM pg_stat_activity
WHERE state = 'idle'
ORDER BY idle_time DESC;
```

### Pool Sizing Formula
```
pool_size = (core_count * 2) + effective_spindle_count
# For SSDs: pool_size = core_count * 2 + 1
# E.g., 4 cores + SSD = 9 connections per pool
```

## Data Integrity Checks

```sql
-- Find orphaned records
SELECT c.id FROM child_table c
LEFT JOIN parent_table p ON c.parent_id = p.id
WHERE p.id IS NULL;

-- Find duplicates
SELECT col, COUNT(*) as cnt
FROM table
GROUP BY col
HAVING COUNT(*) > 1;

-- Validate constraints
ALTER TABLE t VALIDATE CONSTRAINT fk_name;
```

## Rules
- Always `EXPLAIN ANALYZE` before optimizing queries
- Never add indexes without checking write impact
- Migrations must be idempotent and reversible
- Test migrations on production-size data copies
- Monitor connection pool usage, not just errors
- Use `pg_stat_statements` for ongoing query monitoring
- Keep transactions as short as possible
- Prefer optimistic locking over pessimistic for web apps
