# OpenLearn AI — Design Tokens

## 1. Overview

This document defines the shared design tokens for the OpenLearn AI frontend.

The design system is implemented using:

* Tailwind CSS 4
* CSS custom properties
* shadcn/ui
* Light and dark themes
* OKLCH color values

These tokens are the shared UI contract for all future frontend work.

---

## 2. Color System

### Core Colors

| Token                | Purpose                                 |
| -------------------- | --------------------------------------- |
| `background`         | Main application background             |
| `foreground`         | Main application text                   |
| `card`               | Card and elevated surface background    |
| `card-foreground`    | Text displayed on cards                 |
| `popover`            | Popover and floating surface background |
| `popover-foreground` | Text displayed in popovers              |

### Brand Colors

| Token                  | Purpose                                    |
| ---------------------- | ------------------------------------------ |
| `primary`              | Main brand and primary actions             |
| `primary-foreground`   | Content displayed on primary backgrounds   |
| `secondary`            | Secondary actions and surfaces             |
| `secondary-foreground` | Content displayed on secondary backgrounds |
| `accent`               | Highlighted or emphasized UI               |
| `accent-foreground`    | Content displayed on accent backgrounds    |

### Semantic Colors

| Token                | Purpose                                   |
| -------------------- | ----------------------------------------- |
| `success`            | Successful operations and positive states |
| `success-foreground` | Content displayed on success backgrounds  |
| `warning`            | Warnings and attention states             |
| `warning-foreground` | Content displayed on warning backgrounds  |
| `error`              | Errors and destructive states             |
| `error-foreground`   | Content displayed on error backgrounds    |
| `info`               | Informational states                      |
| `info-foreground`    | Content displayed on info backgrounds     |

The existing shadcn `destructive` token maps to the `error` semantic token.

```css
--destructive: var(--error);
```

### Utility Colors

| Token              | Purpose                   |
| ------------------ | ------------------------- |
| `muted`            | Subtle backgrounds        |
| `muted-foreground` | Secondary or subdued text |
| `border`           | Default borders           |
| `input`            | Input borders             |
| `ring`             | Focus indicators          |

---

## 3. Typography

The primary font is Geist Sans.

The monospace font is Geist Mono.

### Typography Scale

| Token       |     Size | Line Height |
| ----------- | -------: | ----------: |
| `text-xs`   |  0.75rem |        1rem |
| `text-sm`   | 0.875rem |     1.25rem |
| `text-base` |     1rem |      1.5rem |
| `text-lg`   | 1.125rem |     1.75rem |
| `text-xl`   |  1.25rem |     1.75rem |
| `text-2xl`  |   1.5rem |        2rem |
| `text-3xl`  | 1.875rem |     2.25rem |
| `text-4xl`  |  2.25rem |      2.5rem |
| `text-5xl`  |     3rem |           1 |

Usage should follow the semantic importance of the content rather than using large sizes purely for visual emphasis.

---

## 4. Spacing

The spacing system follows a consistent 4px base unit.

| Token        |   Value |
| ------------ | ------: |
| `spacing-0`  |       0 |
| `spacing-1`  | 0.25rem |
| `spacing-2`  |  0.5rem |
| `spacing-3`  | 0.75rem |
| `spacing-4`  |    1rem |
| `spacing-5`  | 1.25rem |
| `spacing-6`  |  1.5rem |
| `spacing-8`  |    2rem |
| `spacing-10` |  2.5rem |
| `spacing-12` |    3rem |
| `spacing-16` |    4rem |
| `spacing-20` |    5rem |
| `spacing-24` |    6rem |

Spacing should be selected from this scale whenever possible.

---

## 5. Border Radius

The base radius is:

```css
--radius: 0.625rem;
```

Derived radius tokens are:

| Token        | Value                       |
| ------------ | --------------------------- |
| `radius-sm`  | `calc(var(--radius) * 0.6)` |
| `radius-md`  | `calc(var(--radius) * 0.8)` |
| `radius-lg`  | `var(--radius)`             |
| `radius-xl`  | `calc(var(--radius) * 1.4)` |
| `radius-2xl` | `calc(var(--radius) * 1.8)` |
| `radius-3xl` | `calc(var(--radius) * 2.2)` |
| `radius-4xl` | `calc(var(--radius) * 2.6)` |

---

## 6. Shadows

The shared shadow scale is:

| Token       | Usage                                |
| ----------- | ------------------------------------ |
| `shadow-sm` | Subtle elevation                     |
| `shadow-md` | Cards and standard elevated surfaces |
| `shadow-lg` | Larger elevated components           |
| `shadow-xl` | High-emphasis floating elements      |

Components should avoid arbitrary shadow values unless a specific design requirement exists.

---

## 7. Responsive Breakpoints

The frontend uses the following responsive breakpoints:

| Token |  Width |
| ----- | -----: |
| `sm`  |  640px |
| `md`  |  768px |
| `lg`  | 1024px |
| `xl`  | 1280px |
| `2xl` | 1536px |

The default approach is mobile-first responsive design.

Example:

```tsx
<div className="text-sm md:text-base lg:text-lg">
  Responsive content
</div>
```

---

## 8. Light Theme

The default theme is the light theme.

Light mode uses:

* A near-white application background
* White surfaces
* Indigo as the primary brand color
* Neutral secondary and muted surfaces
* Semantic success, warning, error, and info colors

The primary color is based on an indigo hue.

---

## 9. Dark Theme

Dark mode is activated using the `.dark` class.

Dark mode provides:

* Dark application backgrounds
* Dark elevated surfaces
* Adjusted primary colors for visibility
* Softer borders
* Higher-contrast foreground colors
* Adjusted semantic colors for dark backgrounds

The same semantic token names are used in both themes.

For example:

```css
--primary
--success
--warning
--error
--info
```

Components should therefore never need to know whether the application is currently using light or dark mode.

---

## 10. Tailwind CSS 4 Integration

The design tokens are exposed to Tailwind CSS 4 through the `@theme inline` block in:

```text
frontend/app/globals.css
```

Example:

```css
@theme inline {
  --color-primary: var(--primary);
  --color-success: var(--success);
  --color-warning: var(--warning);
  --color-error: var(--error);
  --color-info: var(--info);
}
```

This allows components to use semantic utility classes such as:

```tsx
bg-primary
text-primary-foreground
bg-success
text-success-foreground
bg-warning
text-warning-foreground
bg-error
text-error-foreground
bg-info
text-info-foreground
```

---

## 11. Theme Usage Rules

### Do

* Use semantic design tokens.
* Use Tailwind utility classes connected to the tokens.
* Use the same token names across light and dark themes.
* Prefer existing spacing, radius, and shadow values.
* Use shadcn/ui components where applicable.
* Keep component styling consistent with the design system.

### Don't

* Hard-code brand colors inside components.
* Introduce arbitrary spacing values without a clear reason.
* Create separate component colors for light and dark mode.
* Override shadcn semantic tokens unnecessarily.
* Introduce new design tokens without documenting them.

---

## 12. Source of Truth

The primary implementation is:

```text
frontend/app/globals.css
```

The documentation is:

```text
docs/design-tokens.md
```

Any future changes to the design system should update both the implementation and this documentation.

---

## 13. Review Status

Status: **Week 2 — Design Token Implementation**

The tokens are implemented using Tailwind CSS 4 and CSS variables.

The frontend production build has been verified successfully after the token implementation.
