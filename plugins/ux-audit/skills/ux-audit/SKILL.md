---
name: ux-audit
description: Perform a UX audit on a web/mobile application checking usability heuristics, accessibility, and user flow quality. Use when reviewing UI/UX of an application.
argument-hint: "[page-or-component-to-audit]"
---

# UX Audit

Audit the UX of: **$ARGUMENTS**

## Audit Framework

### Nielsen's 10 Usability Heuristics

#### 1. Visibility of System Status
- [ ] User knows where they are (breadcrumbs, active nav)
- [ ] Loading states shown for async operations
- [ ] Progress indicators for multi-step processes
- [ ] Success/error feedback after actions
- [ ] Form validation shows inline errors immediately

#### 2. Match Between System & Real World
- [ ] Language is user-friendly (no technical jargon)
- [ ] Icons are recognizable and standard
- [ ] Workflows match user mental models
- [ ] Information organized logically

#### 3. User Control & Freedom
- [ ] Undo/redo available for destructive actions
- [ ] Confirmation dialogs for irreversible actions
- [ ] Easy to navigate back/cancel
- [ ] Can dismiss modals/overlays easily
- [ ] Clear exit points from flows

#### 4. Consistency & Standards
- [ ] Consistent button styles and placement
- [ ] Consistent terminology throughout
- [ ] Platform conventions followed (mobile/web)
- [ ] Color usage consistent (red=error, green=success)

#### 5. Error Prevention
- [ ] Destructive actions require confirmation
- [ ] Input constraints prevent invalid data
- [ ] Defaults are safe and sensible
- [ ] Auto-save for long forms

#### 6. Recognition Over Recall
- [ ] Recently used items shown
- [ ] Search with suggestions/autocomplete
- [ ] Labels on all form fields (not just placeholders)
- [ ] Contextual help available

#### 7. Flexibility & Efficiency
- [ ] Keyboard shortcuts for power users
- [ ] Bulk actions available
- [ ] Filters and sorting on lists
- [ ] Responsive design for all screen sizes

#### 8. Aesthetic & Minimalist Design
- [ ] No visual clutter
- [ ] Clear visual hierarchy
- [ ] Adequate whitespace
- [ ] Focused content per page

#### 9. Error Recovery
- [ ] Error messages explain what went wrong
- [ ] Error messages suggest how to fix it
- [ ] Form errors don't clear valid inputs
- [ ] Can retry failed operations

#### 10. Help & Documentation
- [ ] Tooltips for complex features
- [ ] Onboarding for new users
- [ ] Contextual help (not just docs)
- [ ] FAQ or support access

### Accessibility (WCAG 2.1 AA)
- [ ] Color contrast ratio ≥ 4.5:1 for text
- [ ] All images have alt text
- [ ] Keyboard navigable (Tab, Enter, Escape)
- [ ] Focus indicators visible
- [ ] Form labels associated with inputs
- [ ] ARIA labels on interactive elements
- [ ] No information conveyed by color alone
- [ ] Text resizable to 200% without loss
- [ ] Screen reader compatible

### Mobile Responsiveness
- [ ] Touch targets ≥ 44x44px
- [ ] No horizontal scrolling
- [ ] Readable without zooming
- [ ] Bottom navigation for primary actions
- [ ] Swipe gestures where expected

## Audit Output Format

```markdown
## UX Audit Report

### Overview
- **Component**: [what was audited]
- **Overall Score**: X/10
- **Critical Issues**: X
- **Improvement Opportunities**: X

### Critical Issues (Must Fix)
1. **[Heuristic]** — Description. Impact on users. Suggested fix.

### Major Improvements
1. **[Heuristic]** — Description. Suggested improvement.

### Minor Suggestions
1. **[Heuristic]** — Description.

### Accessibility Issues
1. **[WCAG Criterion]** — Description. Fix.

### What's Working Well
- [Positive patterns observed]
```

## Rules
- Audit from the user's perspective, not the developer's
- Prioritize issues by user impact
- Every issue needs a concrete fix suggestion
- Test with keyboard navigation
- Check on mobile viewport sizes
- Accessibility issues are blocking, not optional
