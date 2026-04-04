---
name: qruiq-review-ux
description: |
  Review-only audit of interaction UX patterns. Scans for missing confirmation dialogs,
  loading states, toast feedback, form validation, empty states, keyboard accessibility,
  error boundaries, progressive disclosure, navigation patterns, responsive touch targets,
  scroll behavior, state persistence, search UX, file upload UX, permission UI,
  and other interaction anti-patterns. Reports issues with severity and recommended fix —
  does NOT modify any code.
  Use when asked to "review UX", "audit interactions", "check UX", "交互审查",
  "优化交互", "交互细节", "UX best practices", "review UI patterns", "检查界面",
  "UI 审查", "交互优化", or any request involving reviewing or improving the quality
  of user-facing interaction flows.
allowed-tools:
  - Read
  - Grep
  - Glob
---

# qruiq-review-ux

> **Review-only.** Audit the current project for interaction anti-patterns and produce a
> structured report with recommendations. This skill never edits code.
>
> Tech stack assumption: Next.js + HeroUI + Tailwind CSS + TypeScript

## Parameters

Collect before execution:

| Parameter | Required | Default | Description |
|---|---|---|---|
| `SCOPE` | No | `full` | Audit scope: `full` (entire app) or a specific directory path (e.g. `app/dashboard`) |

## Steps

**Execute all steps directly. Do not list as TODOs.**

### 1. Scan the project

Identify all interactive elements by searching for:

```bash
# Destructive actions
grep -rn "delete\|remove\|reset\|revoke\|disconnect\|destroy" --include="*.tsx" --include="*.ts"

# Form submissions
grep -rn "onSubmit\|handleSubmit\|action=" --include="*.tsx"

# Buttons and clickable elements
grep -rn "<Button\|<button\|onClick" --include="*.tsx"

# API calls (mutations)
grep -rn "fetch(\|axios\.\|useSWRMutation\|useMutation\|\.post(\|\.put(\|\.delete(\|\.patch(" --include="*.tsx" --include="*.ts"

# Navigation and menus
grep -rn "Dropdown\|Popover\|Menu\|NavBar\|Sidebar\|drawer\|signOut\|logout\|sign.out\|log.out" --include="*.tsx"

# Search inputs
grep -rn "search\|<Input.*type=.search\|useSearch\|onSearch\|debounce" --include="*.tsx" --include="*.ts"

# File uploads
grep -rn "upload\|<input.*type=.file\|FileReader\|FormData\|dropzone\|drag.*drop" --include="*.tsx" --include="*.ts"

# Lists and tables
grep -rn "<Table\|<table\|\.map(\|<Card.*map\|pagination\|Pagination\|infinite" --include="*.tsx"

# Scroll behavior
grep -rn "scroll\|useScroll\|IntersectionObserver\|scrollTo\|overflow" --include="*.tsx" --include="*.ts"

# Route guards and permissions
grep -rn "redirect\|unauthorized\|forbidden\|role\|permission\|isAuth\|isAdmin\|canAccess" --include="*.tsx" --include="*.ts"

# Multi-step flows
grep -rn "step\|wizard\|stepper\|onNext\|onPrev\|currentStep" --include="*.tsx" --include="*.ts"
```

### 2. Audit against the checklist

For each interactive element found, check against the **Interaction Checklist** (categories A–Q) below.
Record all violations as a structured report.

### 3. Output the report

Present a structured report in this format:

```markdown
# UX Interaction Audit Report

## Summary
- Total issues found: N
- P0 Critical: N | P1 High: N | P2 Medium: N | P3 Low: N

## Issues

### P0 Critical

#### 1. [File:Line] Short description
- **Category**: (e.g. A. Destructive Actions)
- **Problem**: What's wrong
- **Recommendation**: How to fix it
- **Code snippet**: The offending code (3-5 lines for context)

### P1 High
...

### P2 Medium
...

### P3 Low
...
```

Severity levels:
- **P0 Critical**: Data loss without confirmation, no error handling on mutations, exposed actions without auth guard
- **P1 High**: Missing loading states, no disabled during submit, no toast feedback, flat info hierarchy exposing destructive/sensitive actions at top level
- **P2 Medium**: Missing empty states, no keyboard support, poor focus management, no search debounce, missing scroll restoration
- **P3 Low**: Missing transitions/animations, tooltip hints, micro-interactions, inconsistent icon-only button hints

**Do NOT apply any fixes. Only report.**

---

## Interaction Checklist

### A. Destructive Actions — Confirmation Required

Any action that deletes, removes, resets, or irreversibly changes data MUST have a confirmation step.

**What to check:**
- `onClick` handlers that call delete/remove APIs without a confirmation modal
- Inline delete buttons without a two-step flow (click → confirm → execute)
- Bulk actions (select all → delete) without explicit count in confirmation

**Expected pattern:**
- Use a Modal or Popover confirmation — never `window.confirm()`
- Confirmation text must name the action and the target (e.g. "Delete project 'My App'?")
- Destructive button must use danger styling and be placed on the right
- Cancel button must be the default focus to prevent accidental confirm
- Must support `Escape` key to cancel

### B. Loading & Disabled States

**What to check:**
- Buttons that trigger async operations without a loading indicator
- Forms that can be double-submitted
- Pages that fetch data without a skeleton or spinner

**Expected pattern:**
- Buttons must show a loading spinner and be disabled while the operation is in-flight
- Form submit buttons must be disabled after first click until the response arrives
- Data loading states should use skeleton layouts matching the final content shape
- Full-page loads should never show a blank white screen — always show a skeleton or spinner

### C. Toast / Feedback Notifications

**What to check:**
- Mutations (create, update, delete) that complete silently with no user feedback
- Error responses that are swallowed or only logged to console

**Expected pattern:**
- Every mutation must show a toast on success AND on failure
- Use a toast library (e.g. `sonner`) — configure once in providers, never use `alert()` or `window.alert()`
- Success toasts should be brief and auto-dismiss in ~3 seconds
- Error toasts should persist until dismissed and include a retry action if applicable

### D. Optimistic Updates

**What to check:**
- Toggle switches, like/favorite buttons, or status changes that wait for API response before reflecting in UI
- Lists where adding/removing items causes a full refetch flash

**Expected pattern:**
- UI-only state changes (toggles, favorites) should update immediately and rollback on error
- List mutations should optimistically add/remove the item without a loading flash
- Show a subtle rollback toast if the optimistic update fails

### E. Form Validation & Error Handling

**What to check:**
- Forms with no client-side validation (relying only on server errors)
- Required fields without visual indicators
- Error messages that appear far from the invalid field
- Forms that clear all input on submission error

**Expected pattern:**
- Required fields must have a visual indicator (asterisk or label text)
- Validate on blur for individual fields, validate all on submit
- Error messages must appear directly below the invalid field
- Form state must be preserved on submission failure — never clear user inputs on error

### F. Empty States

**What to check:**
- Lists or tables that show nothing when data is empty
- Search results with no matches showing a blank area
- Dashboard widgets with no data

**Expected pattern:**
- Every list/table must have an empty state with: illustrative icon + message + primary action button
- Search empty states should suggest clearing filters or broadening the query
- Use a centered layout with muted text

### G. Keyboard Accessibility

**What to check:**
- Custom clickable elements (`<div onClick>`) that are not focusable
- Modals or dropdowns that don't trap focus
- Missing `aria-label` on icon-only buttons

**Expected pattern:**
- All interactive elements must be focusable — use semantic elements (`<button>`, `<a>`) or add `tabIndex={0}` + `role`
- Custom clickable divs must handle `onKeyDown` for Enter and Space
- Modals must trap focus and return focus to the trigger element on close
- Icon-only buttons must have `aria-label`

### H. Error Boundaries

**What to check:**
- Pages or sections that crash the entire app on render error
- Missing error boundaries around dynamic content (user-generated, API-driven)

**Expected pattern:**
- Each route should have a framework-level error boundary (e.g. `error.tsx` in Next.js)
- Critical sections (charts, user content, third-party embeds) should have local error boundaries
- Error UI must offer a "Try again" action and never expose stack traces in production

### I. Transitions & Micro-interactions

**What to check:**
- Elements that appear/disappear instantly (modals, dropdowns, accordions)
- Page transitions that feel jarring
- State changes with no visual continuity

**Expected pattern:**
- Modals and drawers should animate in/out (HeroUI handles this natively)
- List item add/remove should use layout animations for smooth reflows
- Skeleton-to-content transitions should crossfade
- Button state changes (idle → loading → success) should transition smoothly

### J. Progressive Disclosure & Information Hierarchy

Low-frequency or sensitive actions must not sit at the same visual level as primary actions. They should be nested behind an intentional interaction so the interface remains clean and safe.

**What to check:**
- Sign Out / Logout exposed as a top-level button in the header instead of nested inside a user avatar dropdown menu
- "Delete Account" or danger zone settings visible on page load without a collapsed section
- Admin-only actions displayed at the same visual level as regular user actions
- Settings pages that dump all options in a flat list without grouping or collapsible sections
- Edit/Delete actions on cards permanently visible instead of revealed on hover or via a "⋮" overflow menu
- Toolbars with too many visible buttons — low-frequency actions should collapse into a "More" menu

**Expected pattern:**
- Account actions (Sign Out, Profile, Settings) belong inside a Dropdown triggered by the user's avatar — the avatar is the natural affordance for "things about me"
- Destructive settings should be behind a collapsible "Danger Zone" section or placed at the very bottom of the page
- Card action menus: use a three-dot icon button that opens a dropdown; only the primary action (e.g. "Open") should be directly visible on the card surface
- Toolbars with more than 4–5 actions should group lower-priority items into a "More" dropdown
- Inline editing: show read-only content by default; reveal edit controls on hover or via an explicit "Edit" trigger

### K. Navigation & Menu Patterns

**What to check:**
- No visual indicator for the current active route in the sidebar or navbar
- Mobile navigation missing entirely (no hamburger menu, bottom tabs, or drawer)
- Breadcrumbs absent on deeply nested pages (3+ levels deep)
- Logo or app name not linking back to home/dashboard
- Navigation items using plain `<div>` or `<span>` instead of proper link elements

**Expected pattern:**
- Active route must be visually distinct (background highlight, bold text, left border, or underline)
- Mobile screens (< 768px) should collapse navigation into a hamburger/drawer or switch to bottom tabs
- Pages 3+ levels deep should show breadcrumbs for orientation
- The app logo must always link to the root route
- Navigation items must be semantic links for right-click/open-in-new-tab support and accessibility

### L. Responsive & Touch UX

**What to check:**
- Tap targets smaller than 44×44px on interactive elements
- Hover-only interactions with no touch alternative (e.g. tooltip content, hover-reveal menus)
- Content overflow or horizontal scroll on mobile viewports
- Fixed-position elements (modals, floating buttons) that overlap or become unreachable on small screens
- Text inputs that cause layout shifts when the mobile keyboard opens

**Expected pattern:**
- All tappable elements must meet minimum 44×44px (Apple HIG) / 48×48dp (Material) — if the visual element is smaller, add padding to expand the hit area
- Hover-triggered content must also be accessible via tap/click or long-press
- Test layouts at 320px, 375px, and 768px breakpoints — no horizontal overflow
- Modals on mobile should use full-screen or bottom-sheet presentation
- Use `dvh` (dynamic viewport height) units instead of `vh` to account for mobile browser chrome

### M. Search UX

**What to check:**
- Search input that fires a request on every keystroke with no debounce
- No loading indicator while search results are being fetched
- No empty state for "no results found"
- Search input that cannot be cleared with a single action (missing ✕ button)
- No keyboard shortcut to focus search (e.g. `/` or `Cmd+K`)

**Expected pattern:**
- Debounce search input by at least 300ms before triggering a request
- Show a spinner inside or adjacent to the search input while loading
- Empty result state should say "No results for '[query]'" and suggest broadening the search
- Include a clear button (✕) inside the input when it has a value
- Consider supporting `Cmd+K` / `Ctrl+K` or `/` to focus the search field

### N. File Upload UX

**What to check:**
- File input with no drag-and-drop support
- No progress indicator during upload
- No file type or size validation before upload starts
- No preview for image uploads
- No way to remove a selected file before submitting

**Expected pattern:**
- Provide a drop zone with visual feedback (border highlight on drag-over)
- Show upload progress (percentage bar or spinner)
- Validate file type and size client-side before uploading; show an inline error immediately if invalid
- For image files, show a thumbnail preview after selection
- Allow removing or replacing a selected file before final submission

### O. Permission & Authorization UI

**What to check:**
- Pages that flash restricted content before redirecting unauthorized users
- No visible feedback when a user attempts an action they lack permission for
- Admin-only buttons rendered but non-functional for regular users (silent failures)
- Middleware redirects with no explanation — user sees a sudden jump with no context

**Expected pattern:**
- Unauthorized users should never see restricted content flash — use server-side checks or a loading gate
- If a user lacks permission, show a clear message (e.g. "You don't have access. Contact your admin.")
- Actions the user cannot perform should either be hidden entirely or shown as disabled with a tooltip explaining why
- On redirect for authorization failure, land the user on a meaningful page (e.g. a 403 page with next steps), not the homepage with no explanation

### P. Data Table UX

**What to check:**
- Tables with no sorting on columns that are naturally sortable
- No loading state during data refetch (e.g. when changing sort or filter)
- Table content that overflows on mobile without horizontal scroll or responsive fallback
- Bulk selection (checkbox column) without a "Select All" / "Deselect All" toggle
- Pagination controls that don't indicate total count or current position

**Expected pattern:**
- Sortable columns should show a sort indicator (arrow icon) and toggle asc/desc on click
- Wrap table refetch in a loading state — dim the table body or show a subtle overlay spinner
- On mobile, either allow horizontal scroll with a visible scrollbar hint, or switch to a card-based layout
- Bulk selection should include "Select all on this page" and optionally "Select all N items"
- Pagination must show: current page, total pages or total items, and per-page size selector

### Q. Scroll & State Persistence

**What to check:**
- Scroll position lost when navigating back (e.g. list → detail → back resets to top)
- Tab selection, filter values, or sort order that reset on page navigation
- Infinite scroll with no "Back to top" affordance
- Infinite scroll that loses position on page refresh

**Expected pattern:**
- Preserve scroll position on back navigation — verify that the routing approach supports this
- Persist filter, sort, and tab state in URL search params so it survives refresh and is shareable
- Infinite scroll pages should show a floating "Back to top" button after scrolling 2+ viewport heights
- Consider URL-based pagination (e.g. `?page=3`) even in infinite scroll as a fallback anchor

---

## Confirmation Patterns by Action Type

Use this table to verify the correct confirmation pattern is used:

| Action Type | Expected Pattern | Example |
|---|---|---|
| Delete single item | Modal with item name | "Delete user 'John Doe'?" |
| Delete multiple items | Modal with count | "Delete 3 selected projects?" |
| Irreversible action | Modal + type-to-confirm | "Type 'DELETE' to confirm" |
| Logout / disconnect | Dropdown menu item (not top-level button) | Avatar → Menu → "Sign Out" |
| Discard unsaved changes | Modal on navigation | "You have unsaved changes. Discard?" |
| Bulk operation | Modal with summary | "Archive 12 messages?" |
| Payment / charge | Modal with amount | "Charge $49.99 to card ending 4242?" |
| Toggle dangerous setting | Inline confirm with undo window | Switch flips → "Undo" toast for 5s |

---

## Composability

This skill layers on top of existing projects as a review step:

```
qruiq-create-app          → Project skeleton
    + qruiq-review-ux      → Review interaction patterns (report only)
    + qruiq-google-auth    → Google OAuth login
    + qruiq-github-ci      → CI/CD pipeline
```

## Rules

- **NEVER edit, write, or create any file** — this is a review-only skill
- Output a structured report with file paths, line numbers, and severity
- If no issues are found for a category, skip it in the report
- Be specific: cite exact file + line, not vague "some buttons lack loading states"