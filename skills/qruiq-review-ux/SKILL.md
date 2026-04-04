---
name: qruiq-review-ux
description: |
  Review-only audit of interaction UX patterns. Scans for missing confirmation dialogs,
  loading states, toast feedback, form validation, empty states, keyboard accessibility,
  error boundaries, and other interaction anti-patterns. Reports issues with severity
  and recommended fix — does NOT modify any code.
  Use when asked to "review UX", "audit interactions", "check UX", "交互审查",
  "优化交互", "交互细节", or "UX best practices".
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

```
# Destructive actions (delete, remove, reset, revoke, disconnect)
grep -r "delete\|remove\|reset\|revoke\|disconnect\|destroy" --include="*.tsx" --include="*.ts"

# Form submissions
grep -r "onSubmit\|handleSubmit\|action=" --include="*.tsx"

# Buttons and clickable elements
grep -r "<Button\|<button\|onClick" --include="*.tsx"

# API calls (mutations)
grep -r "fetch(\|axios\.\|useSWRMutation\|useMutation\|\.post(\|\.put(\|\.delete(\|\.patch(" --include="*.tsx" --include="*.ts"
```

### 2. Audit against the checklist

For each interactive element found, check against the **Interaction Checklist** below.
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
- **Recommendation**: How to fix it, referencing the pattern from the Reference Patterns section
- **Code snippet**: The offending code (3-5 lines for context)

### P1 High
...

### P2 Medium
...

### P3 Low
...
```

Severity levels:
- **P0 Critical**: Data loss without confirmation, no error handling on mutations
- **P1 High**: Missing loading states, no disabled during submit, no toast feedback
- **P2 Medium**: Missing empty states, no keyboard support, poor focus management
- **P3 Low**: Missing transitions/animations, tooltip hints, micro-interactions

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
- Use a Modal (HeroUI `<Modal>`) or Popover confirmation — NOT `window.confirm()`
- Confirmation text must name the action and the target (e.g. "Delete project 'My App'?")
- Destructive button must be `color="danger"` and placed on the right
- Cancel button must be the default focus (prevent accidental confirm)
- Support `Escape` key to cancel

### B. Loading & Disabled States

**What to check:**
- Buttons that trigger async operations without a loading indicator
- Forms that can be double-submitted
- Pages that fetch data without a skeleton/spinner

**Expected pattern:**
- Button must show `isLoading` spinner and be `isDisabled` while the operation is in-flight
- Form submit buttons must be disabled after first click until response
- Use HeroUI `<Spinner>` or `<Skeleton>` for data loading states
- Full-page loads should use skeleton layouts matching the final content shape

### C. Toast / Feedback Notifications

**What to check:**
- Mutations (create, update, delete) that complete silently with no user feedback
- Error responses that are swallowed or only logged to console

**Expected pattern:**
- Every mutation must show a toast on success AND on failure
- Use a toast library (e.g. `sonner`, `react-hot-toast`) — configure once in providers
- Success toast: brief, auto-dismiss in 3s (e.g. "Project deleted")
- Error toast: persist until dismissed, include retry action if applicable
- Do NOT use `alert()` or `window.alert()`

### D. Optimistic Updates

**What to check:**
- Toggle switches, like/favorite buttons, or status changes that wait for API response
- Lists where adding/removing items causes a full refetch flash

**Expected pattern:**
- UI-only state changes (toggles, favorites) should update immediately and rollback on error
- List mutations should optimistically add/remove the item
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
- Error messages appear directly below the invalid field, in `text-danger`
- Form state must be preserved on submission failure (never clear inputs)
- Use HeroUI `isInvalid` + `errorMessage` props on input components

### F. Empty States

**What to check:**
- Lists/tables that show nothing when data is empty
- Search results with no matches showing a blank area
- Dashboard widgets with no data

**Expected pattern:**
- Every list/table must have an empty state with: icon + message + primary action
- Example: "No projects yet" + [Create Project] button
- Search empty state should suggest clearing filters or broadening the query
- Use a centered layout with muted text and an illustrative icon

### G. Keyboard Accessibility

**What to check:**
- Custom clickable elements (`<div onClick>`) that are not focusable
- Modals/dropdowns that don't trap focus
- Missing `aria-label` on icon-only buttons

**Expected pattern:**
- All interactive elements must be focusable (`<button>`, `<a>`, or `tabIndex={0}` + `role`)
- Custom clickable divs must handle `onKeyDown` for Enter and Space
- Modals must trap focus and return focus to the trigger on close
- Icon-only buttons must have `aria-label`
- Dropdown menus must support arrow key navigation (HeroUI handles this natively)

### H. Error Boundaries

**What to check:**
- Pages/sections that crash the entire app on render error
- Missing error boundaries around dynamic content (user-generated, API-driven)

**Expected pattern:**
- Each route should have an `error.tsx` (Next.js error boundary)
- Critical sections (charts, user content, third-party embeds) should have local error boundaries
- Error UI must offer a "Try again" action and not expose stack traces in production

### I. Transitions & Micro-interactions

**What to check:**
- Elements that appear/disappear instantly (modals, dropdowns, accordions)
- Page transitions that feel jarring
- State changes with no visual continuity

**Expected pattern:**
- Modals/drawers: use HeroUI built-in animations (already included)
- List item add/remove: use `framer-motion` `AnimatePresence` + `layout` for smooth reflows
- Skeleton → content: crossfade transition
- Button state changes (idle → loading → success): smooth icon/text transitions

### J. Confirmation Patterns by Action Type

Use this table to verify the correct confirmation pattern is used:

| Action Type | Expected Pattern | Example |
|---|---|---|
| Delete single item | Modal with item name | "Delete user 'John Doe'?" |
| Delete multiple items | Modal with count | "Delete 3 selected projects?" |
| Irreversible action | Modal + type-to-confirm | "Type 'DELETE' to confirm" |
| Logout / disconnect | Popover confirmation | "Sign out of all devices?" |
| Discard unsaved changes | Modal on navigation | "You have unsaved changes. Discard?" |
| Bulk operation | Modal with summary | "Archive 12 messages?" |
| Payment / charge | Modal with amount | "Charge $49.99 to card ending 4242?" |

---

## Reference Patterns

> These are **examples for the report recommendations**, not code to be applied.

### Pattern: Confirmation Modal for Delete

```tsx
import {
  Modal, ModalContent, ModalHeader, ModalBody, ModalFooter,
  Button, useDisclosure,
} from "@heroui/react";

function DeleteButton({ itemName, onConfirm }: { itemName: string; onConfirm: () => Promise<void> }) {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleConfirm = async (onClose: () => void) => {
    setIsDeleting(true);
    try {
      await onConfirm();
      toast.success(`${itemName} deleted`);
      onClose();
    } catch {
      toast.error(`Failed to delete ${itemName}`);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <Button color="danger" variant="light" onPress={onOpen}>Delete</Button>
      <Modal isOpen={isOpen} onOpenChange={onOpenChange}>
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader>Delete {itemName}?</ModalHeader>
              <ModalBody><p>This action cannot be undone.</p></ModalBody>
              <ModalFooter>
                <Button variant="light" onPress={onClose} autoFocus>Cancel</Button>
                <Button color="danger" onPress={() => handleConfirm(onClose)} isLoading={isDeleting}>Delete</Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
}
```

### Pattern: Submit Button with Loading State

```tsx
function SubmitButton({ children = "Save" }: { children?: string }) {
  const { pending } = useFormStatus();
  return (
    <Button type="submit" color="primary" isLoading={pending} isDisabled={pending}>
      {children}
    </Button>
  );
}
```

### Pattern: Toast Provider Setup (sonner)

```tsx
// app/providers.tsx
import { Toaster } from "sonner";

export function Providers({ children }) {
  return (
    <HeroUIProvider>
      <NextThemesProvider>
        {children}
        <Toaster richColors position="bottom-right" />
      </NextThemesProvider>
    </HeroUIProvider>
  );
}
```

### Pattern: Empty State Component

```tsx
function EmptyState({
  icon: Icon, title, description, action,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  action?: { label: string; onPress: () => void };
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <Icon className="mb-4 h-12 w-12 text-default-300" />
      <h3 className="text-lg font-semibold text-default-700">{title}</h3>
      <p className="mt-1 text-sm text-default-400">{description}</p>
      {action && (
        <Button className="mt-4" color="primary" onPress={action.onPress}>{action.label}</Button>
      )}
    </div>
  );
}
```

### Pattern: Unsaved Changes Guard

```tsx
"use client";
import { useEffect } from "react";

function useUnsavedChangesGuard(isDirty: boolean) {
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (isDirty) { e.preventDefault(); e.returnValue = ""; }
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [isDirty]);
}
```

### Pattern: Type-to-Confirm for High-Risk Actions

```tsx
function TypeToConfirmModal({
  isOpen, onOpenChange, confirmText = "DELETE", onConfirm, title, description,
}: {
  isOpen: boolean; onOpenChange: (open: boolean) => void;
  confirmText?: string; onConfirm: () => Promise<void>;
  title: string; description: string;
}) {
  const [input, setInput] = useState("");
  return (
    <Modal isOpen={isOpen} onOpenChange={onOpenChange}>
      <ModalContent>
        {(onClose) => (
          <>
            <ModalHeader>{title}</ModalHeader>
            <ModalBody>
              <p>{description}</p>
              <p className="mt-2 text-sm text-default-500">
                Type <code className="font-bold text-danger">{confirmText}</code> to confirm:
              </p>
              <Input value={input} onValueChange={setInput} placeholder={confirmText} variant="bordered" />
            </ModalBody>
            <ModalFooter>
              <Button variant="light" onPress={onClose}>Cancel</Button>
              <Button color="danger" isDisabled={input !== confirmText}
                onPress={async () => { await onConfirm(); onClose(); }}>
                Confirm
              </Button>
            </ModalFooter>
          </>
        )}
      </ModalContent>
    </Modal>
  );
}
```

## Composability

This skill layers on top of existing projects as a review step:

```
qruiq-create-app          → Project skeleton
    + qruiq-ux-polish      → Review interaction patterns (report only)
    + qruiq-google-auth    → Google OAuth login
    + qruiq-github-ci      → CI/CD pipeline
```

## Rules

- **NEVER edit, write, or create any file** — this is a review-only skill
- Output a structured report with file paths, line numbers, and severity
- Reference patterns are provided as recommendations, not applied automatically
- If no issues are found for a category, skip it in the report
- Be specific: cite exact file + line, not vague "some buttons lack loading states"
