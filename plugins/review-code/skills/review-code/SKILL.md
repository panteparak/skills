---
name: review-code
description: Perform a thorough code review checking architecture, correctness, security, performance, testing, and code quality. Use when reviewing code changes or pull requests.
argument-hint: "[file-or-pr-to-review]"
---

# Code Review

Review the following code: **$ARGUMENTS**

## Review Process

1. **Understand intent** — what is this change trying to do?
2. **Read all changed files** — understand the full scope
3. **Check each category** below
4. **Output structured review** with severity ratings

## Review Categories

### Architecture & Design (BLOCKING)
- Does it follow the project's established architecture? (DDD, clean architecture, etc.)
- Are module boundaries respected? (no cross-feature dependencies)
- Is dependency direction correct? (domain has no external deps)
- Are abstractions appropriate? (not over/under-engineered)
- Would this be easy to modify or extend later?

### Correctness (BLOCKING)
- Does the code do what it's supposed to?
- Are all edge cases handled?
- Are error paths correct?
- Is state managed correctly? (no race conditions, no stale data)
- Are transactions used correctly?

### Security (BLOCKING)
- Input validation present?
- No injection vulnerabilities?
- Auth/authz enforced?
- No secrets in code?
- No sensitive data in logs?

### Testing (BLOCKING)
- Are there tests for new/changed behavior?
- Do tests cover edge cases and error paths?
- Are tests deterministic and isolated?
- Is test quality good? (not just covering lines, testing behavior)

### Performance (MAJOR)
- Any N+1 queries?
- Unbounded collections or queries?
- Missing pagination?
- Unnecessary allocations in hot paths?
- Appropriate use of caching?
- Missing timeouts on external calls?

### Error Handling (MAJOR)
- Errors typed and structured?
- Domain errors separated from technical errors?
- No swallowed exceptions?
- Consistent error mapping across layers?
- Meaningful error messages?

### Code Quality (MINOR)
- Clear naming (intention-revealing)?
- Functions small and focused?
- No duplication?
- No magic numbers/strings?
- No dead code?
- Comments explain "why", not "what"?

### API Contract (BLOCKING — if API change)
- Backward compatible?
- Request/response schemas correct?
- Error responses documented?
- Versioning applied if breaking?

### Database (BLOCKING — if schema change)
- Migration present and idempotent?
- Rollback strategy?
- Backward compatible?
- Indexes for new query patterns?

## Review Output Format

```markdown
## Review: [Approve / Request Changes / Block]

### Summary
[1-2 sentence overview]

### 🚫 Blocking Issues
1. **[Category]** file:line — Description. Suggested fix.

### ⚠️ Major Issues
1. **[Category]** file:line — Description. Suggested fix.

### 💡 Suggestions
1. **[Category]** file:line — Description.

### ✅ Positive Notes
- [Good patterns observed]
```

## Severity Definitions

| Level | Meaning | Action |
|-------|---------|--------|
| **Blocking** | Bug, security flaw, architectural violation | Must fix before merge |
| **Major** | Performance issue, missing tests, poor error handling | Should fix before merge |
| **Minor** | Style, naming, minor improvements | Nice to have |

## Rules
- Read ALL changed files before commenting
- Be specific — reference file:line
- Every issue needs a suggested fix or direction
- Don't nitpick style if linter handles it
- Acknowledge good work
- Be constructive, not confrontational
- Block only for real issues, not preferences
