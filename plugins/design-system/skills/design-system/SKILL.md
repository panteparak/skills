---
name: design-system
description: Create or audit a design system with consistent components, tokens, and patterns for web/mobile applications. Use when building or reviewing component libraries.
argument-hint: "[action-or-component]"
---

# Design System

Design system task: **$ARGUMENTS**

## Design Token Foundation

### Color Tokens
```css
/* Semantic color tokens — not raw values */
--color-primary: #2563eb;
--color-primary-hover: #1d4ed8;
--color-primary-active: #1e40af;

--color-success: #16a34a;
--color-warning: #d97706;
--color-error: #dc2626;
--color-info: #2563eb;

--color-text-primary: #111827;
--color-text-secondary: #6b7280;
--color-text-disabled: #9ca3af;
--color-text-inverse: #ffffff;

--color-bg-primary: #ffffff;
--color-bg-secondary: #f9fafb;
--color-bg-tertiary: #f3f4f6;

--color-border-default: #e5e7eb;
--color-border-strong: #d1d5db;
```

### Spacing Scale
```css
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

### Typography Scale
```css
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */

--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;

--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
```

### Border Radius
```css
--radius-sm: 0.25rem;
--radius-md: 0.375rem;
--radius-lg: 0.5rem;
--radius-xl: 0.75rem;
--radius-2xl: 1rem;
--radius-full: 9999px;
```

### Shadows
```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
```

## Component Patterns

### Component Anatomy
Every component should have:
1. **Variants** — visual variations (primary, secondary, ghost)
2. **Sizes** — sm, md, lg
3. **States** — default, hover, active, focus, disabled, loading
4. **Accessibility** — ARIA labels, keyboard navigation, focus management

### Component API Guidelines
- Props should be consistent across components
- Use composition over configuration
- Support `className` / `style` for customization
- Forward refs for DOM access
- Support `data-testid` for testing

### Core Components Checklist
- [ ] Button (primary, secondary, ghost, destructive + sizes)
- [ ] Input (text, email, password, number + validation states)
- [ ] Select / Dropdown
- [ ] Checkbox / Radio / Switch
- [ ] TextArea
- [ ] Badge / Tag
- [ ] Avatar
- [ ] Card
- [ ] Modal / Dialog
- [ ] Toast / Notification
- [ ] Alert
- [ ] Table (sortable, paginated)
- [ ] Tabs
- [ ] Breadcrumb
- [ ] Pagination
- [ ] Skeleton / Loading
- [ ] Empty State
- [ ] Error State

## Design System Audit Checklist

### Consistency
- [ ] All components use design tokens (not hardcoded values)
- [ ] Spacing follows the scale
- [ ] Typography follows the scale
- [ ] Color usage follows semantic tokens
- [ ] Border radius consistent

### Accessibility
- [ ] Color contrast AA compliant (4.5:1 text, 3:1 large text)
- [ ] Focus indicators on all interactive elements
- [ ] ARIA labels on icon-only buttons
- [ ] Keyboard navigable
- [ ] Screen reader tested

### Documentation
- [ ] Usage guidelines for each component
- [ ] Do's and Don'ts with examples
- [ ] Props/API documentation
- [ ] Accessibility notes

## Rules
- Use semantic tokens, never raw color values in components
- Every interactive element needs focus, hover, active, disabled states
- Components must be accessible by default (not opt-in)
- Composition over configuration — small composable pieces
- Document every component with examples
- Test components in isolation (Storybook or equivalent)
