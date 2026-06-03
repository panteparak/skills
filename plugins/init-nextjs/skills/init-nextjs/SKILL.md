---
name: init-nextjs
description: Scaffold a new Next.js + React + TypeScript project with proper structure and testing. Use when creating a new frontend web application.
argument-hint: "[project-name]"
disable-model-invocation: true
---

# Initialize Next.js Project

Scaffold a production-grade Next.js application for: **$ARGUMENTS**

## Step 1: Project Generation

Use the official Next.js CLI:

```bash
npx create-next-app@latest $0 \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*"
```

## Step 2: Additional Dependencies

```bash
cd $0
npm install zod react-hook-form @hookform/resolvers
npm install -D vitest @testing-library/react @testing-library/jest-dom \
  @testing-library/user-event @vitejs/plugin-react jsdom \
  prettier prettier-plugin-tailwindcss
```

## Step 3: Project Structure

Organize with feature-based architecture:

```
src/
├── app/                         # Next.js App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page
│   ├── error.tsx                # Error boundary
│   ├── loading.tsx              # Loading UI
│   ├── not-found.tsx            # 404 page
│   ├── (auth)/                  # Route group: auth pages
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/             # Route group: authenticated
│   │   ├── layout.tsx
│   │   └── dashboard/page.tsx
│   └── api/                     # API routes
│       └── health/route.ts
├── features/                    # Feature modules
│   └── <feature>/
│       ├── components/          # Feature-specific components
│       │   ├── feature-form.tsx
│       │   └── feature-list.tsx
│       ├── hooks/               # Feature-specific hooks
│       │   └── use-feature.ts
│       ├── actions/             # Server actions
│       │   └── feature-actions.ts
│       ├── schemas/             # Zod validation schemas
│       │   └── feature-schema.ts
│       ├── types/               # Feature types
│       │   └── index.ts
│       └── __tests__/           # Feature tests
│           ├── feature-form.test.tsx
│           └── use-feature.test.ts
├── components/                  # Shared UI components
│   ├── ui/                      # Primitives (button, input, card)
│   └── layout/                  # Layout components (header, sidebar)
├── lib/                         # Shared utilities
│   ├── api-client.ts            # Fetch wrapper with error handling
│   ├── utils.ts                 # Generic helpers
│   └── constants.ts
├── hooks/                       # Shared hooks
│   └── use-debounce.ts
└── types/                       # Global types
    └── index.ts
```

## Step 4: Configuration Files

Create:
- `vitest.config.ts` with React + jsdom setup
- `.prettierrc` with Tailwind plugin
- `tsconfig.json` path aliases
- `.env.local.example` with required env vars
- `.eslintrc.json` with strict rules

## Step 5: Base Components & Utilities

Create:
- API client with typed error handling and request/response interceptors
- Zod schema helpers for form validation
- Error boundary component
- Loading skeleton components
- `cn()` utility for Tailwind class merging (clsx + tailwind-merge)

## Step 6: Test Infrastructure

Set up:
- `vitest.config.ts` with React Testing Library
- `src/test/setup.ts` with jest-dom matchers
- Example component test with user interaction
- Example hook test
- Test utilities (render with providers, mock router)

## Step 7: TDD Starter

Create a sample feature (e.g., health status page) with:
1. Failing component test
2. Component implementation
3. Refactor

## Step 8: Documentation & Tooling

- `README.md` with setup, run, test, build, deploy instructions
- npm scripts: `dev`, `build`, `test`, `test:watch`, `lint`, `format`

## Rules
- Server Components by default, Client Components only when needed
- Validate all inputs with Zod schemas
- Use Server Actions for mutations
- Colocate tests with features
- Prefer composition over prop drilling
- Use TypeScript strict mode
- No `any` types — use `unknown` and narrow
