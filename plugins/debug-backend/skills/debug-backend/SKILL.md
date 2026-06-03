---
name: debug-backend
description: Systematically debug backend issues in any language using structured root cause analysis. Use when investigating bugs, errors, or unexpected behavior in backend services.
argument-hint: "[error-or-symptom-description]"
---

# Backend Debugging

Investigate and fix: **$ARGUMENTS**

## Systematic Debugging Process

### Phase 1: Reproduce & Understand
1. **Read the error** — full stack trace, error message, HTTP status
2. **Reproduce** — find minimal steps to trigger the issue
3. **Identify the scope** — which layer? (transport, application, domain, infrastructure)
4. **Check recent changes** — `git log --oneline -20`, `git diff HEAD~5`

### Phase 2: Isolate
5. **Trace the request flow** — entry point → handler → service → repository → DB
6. **Check logs** — filter by correlation ID, timestamp, error level
7. **Inspect data** — verify DB state, cache state, message queue state
8. **Check external dependencies** — is the DB up? Is the external API responding?

### Phase 3: Root Cause Analysis
9. **Form hypothesis** — based on evidence, what's the most likely cause?
10. **Test hypothesis** — add targeted logging, reproduce, verify
11. **Identify root cause** — not the symptom, the underlying issue

### Phase 4: Fix & Verify
12. **Write a failing test** that reproduces the bug
13. **Fix the root cause** — minimal change
14. **Verify the test passes**
15. **Check for similar issues** — does this pattern exist elsewhere?

## Common Backend Bug Patterns

### N+1 Query Problem
**Symptom**: Slow response, many DB queries for a list endpoint
**Check**: Enable query logging, count queries per request
**Fix**: Add `select_related`/`prefetch_related` (Django), `JOIN FETCH` (JPA), or eager loading

### Race Condition
**Symptom**: Intermittent failures, inconsistent data
**Check**: Look for shared mutable state, concurrent DB updates without locking
**Fix**: Use optimistic locking (version column), transactions, or mutex

### Connection Pool Exhaustion
**Symptom**: Timeouts, "cannot acquire connection" errors
**Check**: Monitor active/idle connections, check for leaked connections
**Fix**: Ensure connections are returned (try-with-resources), tune pool size

### Serialization/Deserialization Errors
**Symptom**: 400/500 on API calls, null fields
**Check**: Compare request payload with expected schema, check date formats
**Fix**: Add explicit serializers, validate input schemas

### Transaction Issues
**Symptom**: Partial data saved, inconsistent state
**Check**: Transaction boundaries, nested transactions, propagation settings
**Fix**: Ensure atomic operations are in a single transaction

### Memory Leak
**Symptom**: Increasing memory usage over time, OOM kills
**Check**: Heap dumps, growing collections, unclosed resources
**Fix**: Close resources (streams, connections), bound caches, use weak references

### Authentication/Authorization Failure
**Symptom**: 401/403 errors
**Check**: Token expiry, CORS headers, cookie settings, role mappings
**Fix**: Verify auth config, check token claims, review permission rules

## Debugging Commands

### Logs
```bash
# Tail application logs (Docker)
docker compose logs -f --tail=100 <service>
# Filter by error level
docker compose logs <service> 2>&1 | grep -i error
# Filter by correlation ID
docker compose logs <service> 2>&1 | grep "correlation-id-here"
```

### Database
```sql
-- Check recent modifications
SELECT * FROM <table> ORDER BY updated_at DESC LIMIT 10;
-- Check locks (PostgreSQL)
SELECT * FROM pg_locks WHERE granted = false;
-- Check active connections
SELECT count(*) FROM pg_stat_activity;
```

### Network
```bash
# Check if service is reachable
curl -v http://localhost:8080/health
# Check DNS resolution
nslookup <service-name>
# Check port availability
lsof -i :8080
```

## Rules
- Always reproduce before fixing
- Find root cause, not symptoms
- Write a test that catches the bug before fixing
- Minimal fix — don't refactor during debugging
- Check for similar patterns elsewhere after fixing
- Document non-obvious bugs in code comments or ADRs
