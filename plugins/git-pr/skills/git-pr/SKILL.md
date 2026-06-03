---
name: git-pr
description: Create well-structured pull requests with proper title, description, and test plan using the gh CLI. Use when creating or updating pull requests.
argument-hint: "[optional-base-branch]"
disable-model-invocation: true
---

# Create Pull Request

Create a pull request. Base branch hint: **$ARGUMENTS**

## Process

### Step 1: Analyze All Changes
```bash
# Understand full scope of changes
git status
git log --oneline main..HEAD  # or appropriate base branch
git diff main...HEAD --stat
git diff main...HEAD
```

Review ALL commits (not just latest) to understand the full PR scope.

### Step 2: Ensure Branch is Ready
```bash
# Check if branch tracks remote and is pushed
git branch -vv
# Push if needed
git push -u origin $(git branch --show-current)
```

### Step 3: Determine PR Type
Based on the changes, identify:
- **Feature**: New functionality
- **Fix**: Bug fix
- **Refactor**: Code improvement without behavior change
- **Chore**: Dependencies, CI, tooling
- **Docs**: Documentation updates

### Step 4: Create PR

```bash
gh pr create --title "<type>(<scope>): <concise title>" --body "$(cat <<'EOF'
## Summary
- [What was done and why — 1-3 bullet points]

## Changes
- [List of significant changes]

## Type
- [ ] Feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Chore
- [ ] Docs

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated (if applicable)
- [ ] No breaking changes (or documented below)
- [ ] Self-reviewed the diff

## Test Plan
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing: [describe steps]

## Screenshots
[If UI changes, include before/after]

## Breaking Changes
[List any breaking changes and migration steps, or "None"]

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### Step 5: Verify
```bash
gh pr view --web  # Open in browser to verify
```

## PR Title Rules
- Under 72 characters
- Use conventional commit format: `feat(scope): description`
- Imperative mood: "add" not "added"
- No period at the end

## PR Body Rules
- Summary explains WHY, not just WHAT
- Changes list is scannable
- Test plan is actionable
- Breaking changes are explicit
- Link related issues with `Closes #123` or `Fixes #456`

## Rules
- Review ALL commits in the PR, not just the latest
- PR should be reviewable in one sitting (< 400 lines ideally)
- If PR is large, suggest splitting into smaller PRs
- Never force-push to shared branches
- Always push before creating PR
- Include test plan with specific verification steps
