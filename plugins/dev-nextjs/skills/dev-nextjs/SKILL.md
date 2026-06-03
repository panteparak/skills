---
name: dev-nextjs
description: Develop features in Next.js + React + TypeScript projects with App Router, Server Components, and testing. Use when writing Next.js frontend code.
argument-hint: "[feature-description]"
---

# Next.js + React Development

Implement the following feature: **$ARGUMENTS**

## Development Workflow

1. **Write failing test** — component or hook test
2. **Implement component** — Server Component by default
3. **Add interactivity** — Client Component only when needed
4. **Write integration test** — user flow test
5. **Refactor** — extract shared patterns

## Architecture Decisions

### Server vs Client Components

**Server Components (default):**
- Data fetching
- Accessing backend resources
- Rendering static or server-generated content
- Keeping bundle size small

**Client Components (`"use client"`):**
- User interactions (onClick, onChange)
- Browser APIs (localStorage, geolocation)
- State management (useState, useReducer)
- Effects (useEffect)

```tsx
// Server Component (default) — fetches data
async function OrderList() {
  const orders = await getOrders() // Direct DB/API call
  return (
    <div>
      {orders.map(order => (
        <OrderCard key={order.id} order={order} />
      ))}
    </div>
  )
}

// Client Component — handles interaction
"use client"
function OrderActions({ orderId }: { orderId: string }) {
  const [isPending, startTransition] = useTransition()
  return (
    <button
      disabled={isPending}
      onClick={() => startTransition(() => cancelOrder(orderId))}
    >
      Cancel Order
    </button>
  )
}
```

### Server Actions for Mutations

```tsx
// features/orders/actions/order-actions.ts
"use server"

import { revalidatePath } from "next/cache"
import { z } from "zod"

const CreateOrderSchema = z.object({
  items: z.array(z.object({
    productId: z.string(),
    quantity: z.number().min(1),
  })).min(1),
})

export async function createOrder(formData: FormData) {
  const parsed = CreateOrderSchema.safeParse(Object.fromEntries(formData))
  if (!parsed.success) {
    return { error: parsed.error.flatten().fieldErrors }
  }
  const order = await db.orders.create(parsed.data)
  revalidatePath("/orders")
  redirect(`/orders/${order.id}`)
}
```

### Data Fetching Patterns

```tsx
// Parallel data fetching in Server Components
async function DashboardPage() {
  const [orders, stats, notifications] = await Promise.all([
    getRecentOrders(),
    getDashboardStats(),
    getNotifications(),
  ])
  return (
    <Dashboard orders={orders} stats={stats} notifications={notifications} />
  )
}
```

### Form Handling with Zod + React Hook Form

```tsx
"use client"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"

const schema = z.object({
  email: z.string().email("Invalid email"),
  name: z.string().min(2, "Name too short"),
})

type FormData = z.infer<typeof schema>

function CreateUserForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })
  const onSubmit = async (data: FormData) => {
    await createUser(data)
  }
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register("email")} />
      {errors.email && <span>{errors.email.message}</span>}
      {/* ... */}
    </form>
  )
}
```

## Testing Patterns

```tsx
// Component test
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

describe("OrderActions", () => {
  it("should disable button while cancelling", async () => {
    const user = userEvent.setup()
    render(<OrderActions orderId="123" />)
    const button = screen.getByRole("button", { name: /cancel/i })
    await user.click(button)
    expect(button).toBeDisabled()
  })
})

// Hook test
import { renderHook, act } from "@testing-library/react"

describe("useDebounce", () => {
  it("should debounce value changes", async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: "initial" } }
    )
    rerender({ value: "updated" })
    expect(result.current).toBe("initial")
    await act(() => vi.advanceTimersByTime(300))
    expect(result.current).toBe("updated")
  })
})
```

## Rules
- Server Components by default — add `"use client"` only when required
- Validate all inputs with Zod
- Use Server Actions for mutations (not API routes)
- Colocate tests with features in `__tests__/` directories
- No `any` types — use `unknown` and type-narrow
- Use `Suspense` + `loading.tsx` for loading states
- Use `error.tsx` for error boundaries
- Fetch data in Server Components, pass to Client as props
- Use `React.cache()` or `unstable_cache()` for request deduplication
