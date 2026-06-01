# ExecutiveAI — Design System

## Color Palette

### Brand Colors

| Token                  | Light Mode   | Dark Mode    | Usage                              |
|------------------------|--------------|--------------|-------------------------------------|
| `--color-primary`      | `#2563EB`    | `#3B82F6`    | CTAs, links, active states         |
| `--color-secondary`    | `#7C3AED`    | `#8B5CF6`    | AI features, accent elements       |
| `--color-success`      | `#16A34A`    | `#22C55E`    | Positive trends, healthy inventory |
| `--color-warning`      | `#D97706`    | `#F59E0B`    | Low stock, approaching limits      |
| `--color-danger`       | `#DC2626`    | `#EF4444`    | Errors, negative trends            |

### Neutral / Surface Colors (Dark Mode)

| Token                    | Value       | Usage                               |
|--------------------------|-------------|-------------------------------------|
| `--color-bg`             | `#0F172A`   | Page background                     |
| `--color-surface`        | `#1E293B`   | Card, panel backgrounds             |
| `--color-border`         | `#334155`   | Dividers, input borders             |
| `--color-text-primary`   | `#F1F5F9`   | Body text, headings                 |
| `--color-text-secondary` | `#94A3B8`   | Labels, captions, metadata          |

---

## Typography

- **Primary font**: Inter (UI text)
- **Monospace**: JetBrains Mono (code, AI responses)

### Type Scale

| Token      | Size | Weight | Usage                          |
|------------|------|--------|--------------------------------|
| `text-xs`  | 12px | 400    | Captions, timestamps, badges   |
| `text-sm`  | 14px | 400    | Labels, table cells            |
| `text-base`| 16px | 400    | Body copy, form inputs         |
| `text-xl`  | 20px | 600    | Card titles, dialog headings   |
| `text-3xl` | 30px | 700    | KPI values (primary metric)    |

---

## Dashboard Layout

```
┌────────────────────────────────────────────────────────────┐
│  SIDEBAR  │              MAIN CONTENT AREA                  │
│  (256px)  │  ┌──────────────────────────────────────────┐  │
│           │  │           PAGE HEADER                    │  │
│           │  └──────────────────────────────────────────┘  │
│           │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐          │
│           │  │ KPI  │ │ KPI  │ │ KPI  │ │ KPI  │          │
│           │  └──────┘ └──────┘ └──────┘ └──────┘          │
│           │  ┌─────────────────────┐ ┌──────────────────┐  │
│           │  │   Revenue Chart     │ │  Pipeline Chart  │  │
│           │  │   (2/3 width)       │ │  (1/3 width)     │  │
│           │  └─────────────────────┘ └──────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Responsive Breakpoints

| Breakpoint | Width  | KPI Cards | Chart Layout         |
|------------|--------|-----------|----------------------|
| Mobile     | < 640px| 1 column  | Stacked full-width   |
| Tablet     | 640px+ | 2 columns | Stacked full-width   |
| Desktop    | 1024px+| 4 columns | Side-by-side (2/3 + 1/3) |

---

## Chart Guidelines

| Data Type                | Recommended Chart        |
|--------------------------|--------------------------|
| Time-series / trend      | Line chart               |
| Comparison across items  | Bar chart (horizontal)   |
| Part-of-whole            | Donut chart (max 5 slices)|
| Pipeline / funnel        | Funnel chart             |

- **Gridlines**: light, horizontal only
- **Tooltips**: show date, value, and percent change on hover
- **Animation**: 600ms ease-out on mount
- **Forecast confidence bands**: shaded area at 20% opacity fill

---

## Dark Mode

ExecutiveAI uses **CSS custom properties + Tailwind's `dark:` class strategy**.

```css
:root {
  --color-bg:           #F8FAFC;
  --color-surface:      #FFFFFF;
  --color-text-primary: #0F172A;
  --color-primary:      #2563EB;
}

.dark {
  --color-bg:           #0F172A;
  --color-surface:      #1E293B;
  --color-text-primary: #F1F5F9;
  --color-primary:      #3B82F6;
}
```

User preference stored in `localStorage`. Falls back to OS `prefers-color-scheme`.
