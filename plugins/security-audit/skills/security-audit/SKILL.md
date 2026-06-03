---
name: security-audit
description: Perform a security audit on code, checking for OWASP Top 10, injection, auth issues, secrets, and data exposure. Use when reviewing code for security vulnerabilities.
argument-hint: "[file-or-component-to-audit]"
---

# Security Audit

Perform a security audit on: **$ARGUMENTS**

## Audit Process

1. **Read all source code** in the target scope
2. **Map the attack surface** — inputs, outputs, auth boundaries
3. **Run OWASP Top 10 checklist** against the code
4. **Check for secrets and sensitive data** exposure
5. **Report findings** with severity and remediation

## OWASP Top 10 Checklist (2021)

### A01: Broken Access Control (CRITICAL)
- [ ] Authorization checked server-side on every endpoint
- [ ] No IDOR (Insecure Direct Object Reference) — user can only access their own data
- [ ] Admin endpoints properly restricted
- [ ] CORS configured restrictively (not `*`)
- [ ] Rate limiting on authentication endpoints
- [ ] No privilege escalation paths

### A02: Cryptographic Failures (CRITICAL)
- [ ] Sensitive data encrypted at rest
- [ ] TLS enforced for data in transit
- [ ] No weak algorithms (MD5, SHA1 for passwords)
- [ ] Passwords hashed with bcrypt/scrypt/argon2
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] Proper key management (not in code)

### A03: Injection (CRITICAL)
- [ ] SQL injection — parameterized queries everywhere
- [ ] Command injection — no shell execution with user input
- [ ] LDAP injection — sanitized LDAP queries
- [ ] Template injection — sandboxed template engines
- [ ] XSS — output encoding, CSP headers
- [ ] NoSQL injection — validated query operators

### A04: Insecure Design (HIGH)
- [ ] Threat modeling performed
- [ ] Business logic abuse prevented (rate limits, validation)
- [ ] Security requirements defined
- [ ] Secure defaults used

### A05: Security Misconfiguration (HIGH)
- [ ] Debug mode disabled in production
- [ ] Default credentials changed
- [ ] Error messages don't reveal internals
- [ ] Unnecessary features/ports/services disabled
- [ ] Security headers set (HSTS, CSP, X-Frame-Options)

### A06: Vulnerable Components (HIGH)
- [ ] Dependencies up to date
- [ ] No known CVEs in dependencies
- [ ] Minimal dependency footprint
- [ ] Dependency scanning in CI/CD

### A07: Auth Failures (CRITICAL)
- [ ] Multi-factor authentication available
- [ ] No default/weak passwords allowed
- [ ] Account lockout after failed attempts
- [ ] Session management secure (HTTPOnly, Secure, SameSite cookies)
- [ ] Token expiry and refresh implemented
- [ ] Logout invalidates session/token server-side

### A08: Data Integrity Failures (HIGH)
- [ ] CI/CD pipeline secured
- [ ] Dependencies verified (checksums/signatures)
- [ ] Deserialization of untrusted data avoided
- [ ] Software updates verified

### A09: Logging & Monitoring Failures (MEDIUM)
- [ ] Auth events logged (login, failed login, logout)
- [ ] Access control failures logged
- [ ] Input validation failures logged
- [ ] Sensitive data NOT logged (passwords, tokens, PII)
- [ ] Logs tamper-resistant

### A10: SSRF (HIGH)
- [ ] URL validation on server-side requests
- [ ] Allowlisting for external service URLs
- [ ] No user-controlled URLs in server requests without validation
- [ ] Internal network not accessible via SSRF

## Secret Detection

Search for:
```
- API keys, tokens, passwords in source code
- .env files committed to git
- Hardcoded connection strings
- Private keys or certificates
- AWS/GCP/Azure credentials
```

## Report Format

```markdown
## Security Audit Report

### Summary
- **Scope**: [files/components audited]
- **Risk Level**: CRITICAL / HIGH / MEDIUM / LOW
- **Findings**: X critical, Y high, Z medium

### Critical Findings
#### [CVE-ID or Finding Name]
- **Severity**: CRITICAL
- **Location**: file:line
- **Description**: What's wrong
- **Impact**: What could happen
- **Remediation**: How to fix
- **Code Example**: Before → After

### High Findings
...

### Positive Practices
- [Things done well]
```

## Rules
- Assume hostile inputs and environments
- Every finding needs severity + remediation
- Critical and high findings must block deployment
- Do not accept "we'll fix later" for critical issues
- Check both code AND configuration
- Verify, don't assume — read the actual code
