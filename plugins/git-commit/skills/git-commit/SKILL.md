---
name: git-commit
description: Create well-structured git commits with conventional commit messages, proper staging, and pre-commit checks. Use when committing code changes.
argument-hint: "[optional-commit-scope]"
disable-model-invocation: true
---

# Smart Git Commit

Create a well-structured commit for the current changes. Scope hint: **$ARGUMENTS**

## Process

### Step 1: Analyze Changes
```bash
git status
git diff --staged
git diff
```

Review all changes to understand:
- What was changed and why
- Which files are related (should be in same commit)
- Whether changes should be split into multiple commits

### Step 2: Stage Related Changes
Group related changes into a single commit. If changes span multiple concerns, suggest splitting into multiple commits.

```bash
# Stage specific files — NEVER use `git add .` or `git add -A`
git add <specific-files>
```

**Do NOT stage:**
- `.env` files or credentials
- Generated files (unless intentional)
- Unrelated formatting changes
- Debug/console.log statements

### Step 3: Write Commit Message

Use **Conventional Commits** format:

```
<type>(<scope>): <short summary>

<body — explain WHY, not WHAT>

<footer — breaking changes, issue refs>
```

### Types
| Type | When |
|------|------|
| `feat` | New feature for the user |
| `fix` | Bug fix |
| `refactor` | Code change that neither fixes nor adds feature |
| `test` | Adding or updating tests |
| `docs` | Documentation changes |
| `style` | Formatting, missing semicolons (no logic change) |
| `perf` | Performance improvement |
| `ci` | CI/CD changes |
| `chore` | Build process, dependency updates |
| `revert` | Reverting a previous commit |

### Scope
Use the feature/module name: `feat(auth)`, `fix(orders)`, `refactor(api)`

### Examples

```
feat(orders): add order cancellation endpoint

Allow authenticated users to cancel pending orders via
DELETE /api/v1/orders/{id}. Orders can only be cancelled
while in PENDING or CONFIRMED status.

Closes #142
```

```
fix(auth): prevent token reuse after logout

Previously, JWT tokens remained valid after logout.
Now tokens are added to a blocklist on logout and
checked during authentication.

BREAKING CHANGE: Logout now requires a valid token in
the Authorization header.
```

### Step 4: Commit
```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <summary>

<body>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

### Step 5: Verify
```bash
git log --oneline -5
git status
```

## Rules
- One commit = one logical change
- Write the "why" in the body, not the "what" (the diff shows what)
- Keep subject line under 72 characters
- Use imperative mood: "add feature" not "added feature"
- Never commit secrets, credentials, or .env files
- Never use `--no-verify` to skip pre-commit hooks
- Never amend published commits without explicit user request
- Stage specific files, not `git add .`
- If pre-commit hook fails, fix the issue and create a NEW commit
