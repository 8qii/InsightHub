# InsightHub Frontend Design System

## Purpose

The design system provides a stable visual and component foundation for the Next.js application in `apps/web`. It supports an enterprise intelligence workspace without coupling generic UI primitives to backend contracts or page-specific business logic.

Phase 10.0 established the primitive foundation. Phase 10.1 added the enterprise application shell, and Phase 10.4.5 refined hierarchy and surface depth without changing API behavior or business logic.

## Design Principles

1. **Evidence first**: content, metrics, citations, and execution details remain visually prominent and easy to scan.
2. **Calm enterprise UI**: neutral surfaces and restrained teal and amber accents communicate status without visual noise.
3. **Semantic styling**: components use purpose-based tokens such as `brand`, `surface`, `line`, and `muted` instead of raw color values.
4. **Small composable components**: primitives own presentation; feature components own business meaning; pages own composition and data loading.
5. **Accessible defaults**: interactive elements retain visible focus treatment, semantic HTML, disabled states, and appropriate labels.
6. **Incremental adoption**: existing behavior is preserved, and the `components/ui.tsx` compatibility barrel avoids unnecessary migration churn.

## Component Architecture

```text
apps/web/components/
  ui/             Generic visual primitives
  layout/         Application shell and navigation elements
  intelligence/   Reusable business-intelligence presentation
  charts/         Typed, non-arbitrary chart renderers
  chat/           Analyst chat feature components
  dashboard/      Dashboard page composition
```

Dependency direction should generally flow from feature components to intelligence/layout components and then to UI primitives. Generic UI components must not import feature or API modules.

The intelligence workspace uses focused presentation components:

- `DriverAnalysis`: functional assessment across Sales, Returns, Discounts, and Inventory
- `InvestigationCard`: suggested follow-up question and its decision rationale
- `InvestigationView`: a bounded signal workspace with conclusion, drivers, evidence, and follow-up questions
- `FindingCard`, `DriverBreakdown`, `EvidenceTimeline`, and `QuestionSuggestion`: investigation-specific presentations that keep calculated inputs separate from supporting context
- `InsightHero`, `ConfidenceIndicator`, `EvidenceSummary`, and `RecommendationBlock`: reusable analyst-report elements for the executive briefing
- `InvestigationStatusIndicator` and `InvestigationActivityTimeline`: workflow elements for lifecycle state and chronological decision milestones

The Overview intentionally uses a briefing document structure rather than generic intelligence cards. It owns the single `/api/v1/overview` request and its loading and error states.

The Overview does not render API contracts directly. `apps/web/lib/intelligence-presentation/` converts the stable Overview response into `InsightPresentation`, `AttentionItemPresentation`, and `EvidenceRelationshipPresentation` contracts. This layer owns narrative ordering, evidence relationships, display formatting, and action destinations while leaving backend and agent contracts unchanged.

Overview reading order is insight-first:

```text
Insight hero
  -> finding-to-evidence relationship
  -> supporting context
  -> attention queue
```

Metrics provide context after the conclusion and should not lead the page or require the reader to infer the primary finding.

The executive briefing header is derived from the presentation layer: its company context uses the API-provided scope, while period, evidence count, and preparation status are computed from the Overview response. Loading and empty states should describe the analyst workflow, such as reviewing context and linking evidence, rather than showing generic dashboard placeholders.

The Signals workspace uses Overview signals as its server-provided queue and stores only workflow state in browser-local persistence. Investigation status, opens, completed analysis, and status changes are local interaction records; they do not modify source data or imply authenticated ownership.

## Application Shell

Both routes render inside `AppShell`, which owns the responsive workspace structure:

- `Sidebar`: fixed desktop navigation and an overlay drawer below the desktop breakpoint
- `TopContextBar`: persistent company, reporting period, page scope, and freshness context
- `WorkspaceContainer`: wide, responsive content gutters without a centered maximum width
- `AppShell`: composes navigation, context, and page content while keeping feature data loading inside each page component

```tsx
import { AppShell } from "@/components/layout/app-shell";

<AppShell page="Overview" scope="Product Luna">
  <DashboardContent />
</AppShell>
```

Only implemented destinations are links. Future destinations render as disabled placeholders so navigation does not imply nonexistent routes.

### Responsive Behavior

- Desktop: fixed 16rem sidebar, sticky context bar, and full-width analytical workspace
- Tablet: menu button opens the sidebar as an overlay drawer
- Mobile: context fields use a two-column grid and page content stacks vertically

## Design Tokens

Tokens are defined in `apps/web/app/globals.css` with Tailwind CSS 4 `@theme` variables. They are available as CSS custom properties and semantic Tailwind utilities.

### Colors

- Content: `ink`, `ink-soft`, `muted`, `placeholder`
- Surfaces: `canvas`, `surface`, `surface-subtle`, `surface-muted`
- Borders: `line`, `line-strong`
- Brand: `brand`, `brand-strong`, `brand-muted`, `brand-border`, `brand-soft`, `brand-subtle`
- Status: `warning`, `warning-*`, `danger`, `danger-*`

Use `text-ink`, `bg-surface`, and `border-line` rather than literal hexadecimal utilities. Status colors must communicate a real state, not decoration alone.

### Typography

- `font-sans`: application font stack
- `text-label`: compact section label size
- `text-brand-caption`: logo caption size
- `tracking-label`: uppercase label tracking
- `tracking-eyebrow`: compact badge and supporting-label tracking
- `tracking-brand`: wordmark tracking
- `tracking-heading`: display heading tracking

Use normal Tailwind type sizes for general content and the named tokens for repeated brand or hierarchy roles.

### Spacing

- `page-mobile` and `page-desktop`: application gutters
- `section`: major vertical separation
- `card`: standard card inset

Tailwind's base spacing scale remains valid for local layout. Add a named spacing token only when a value represents a repeated system-level role.

### Borders, Radius, and Shadows

- `line` and `line-strong`: standard and emphasized borders
- `rounded-action`: compact links and controls
- `rounded-control`: form controls, notices, and nested panels
- `rounded-card`: primary container radius
- `shadow-card`: low-elevation panel shadow
- `shadow-editorial`: restrained elevation for primary briefing and decision surfaces
- `shadow-focus`: brand focus treatment

### Surface Hierarchy

Use three visual levels to prevent every section from carrying equal weight:

1. **Primary editorial surface**: page introductions, priority signals, and investigation conclusions. Use `Card` with `tone="editorial"`, a restrained semantic accent, and `shadow-editorial` only when the content should lead the reading order.
2. **Information card**: metrics, findings, and actionable pathways. Use the default `Card` treatment with a concise accent, strong title, and clear interpretation or action.
3. **Utility/supporting card**: evidence, structured driver rows, traces, and secondary context. Use `tone="utility"` so these elements remain readable without competing with decisions.

Status color communicates meaning rather than decoration. Teal marks current or positive information, amber marks watch conditions, and red marks material risk. Avoid applying tinted backgrounds to entire page regions unless the region is intentionally editorial.

## Primitive Usage

### Card

`Card` is the default content container. It renders a semantic `section`, accepts standard HTML attributes, and supports `default`, `brand`, `editorial`, and `utility` tones. Use `editorial` sparingly for conclusions and priority content; use `utility` for supporting evidence and structured context.

```tsx
import { Card } from "@/components/ui/card";

<Card tone="brand" className="p-6">Content</Card>
```

### Badge

`Badge` presents compact metadata or status. Available tones are `brand`, `neutral`, and `warning`; the `compact` option reduces vertical padding for dense contexts.

```tsx
import { Badge } from "@/components/ui/badge";

<Badge tone="brand">Q2 → Q3</Badge>
```

### Button

`Button` provides consistent native button behavior. Variants are `primary`, `secondary`, and `ghost`; sizes are `sm` and `md`. Use a normal Next.js `Link` for navigation rather than nesting links inside buttons.

```tsx
import { Button } from "@/components/ui/button";

<Button type="submit" disabled={loading}>Run analysis</Button>
```

### MetricCard

`MetricCard` belongs to `components/intelligence` because it represents a business metric rather than a generic surface. Use `brand` for standard metrics and `warning` for risk or control metrics.

```tsx
import { MetricCard } from "@/components/intelligence/metric-card";

<MetricCard label="Q3 revenue" value="$246,000" detail="Product Luna · Q3" />
```

### SectionHeader

`SectionHeader` creates consistent page or major-section hierarchy with optional eyebrow, description, and action content. `SectionLabel` remains available for compact labels inside cards.

```tsx
import { SectionHeader } from "@/components/ui/section-header";

<SectionHeader eyebrow="Executive overview" title="Business pulse" description="Current operating signals." />
```

### EmptyState

`EmptyState` communicates a valid absence of content. Use it instead of duplicating dashed placeholder panels. Errors and loading states should remain distinct because they require different semantics.

```tsx
import { EmptyState } from "@/components/ui/empty-state";

<EmptyState title="No citations were returned for this answer." />
```

## Naming Conventions

- Use PascalCase for React components and kebab-case for component filenames.
- Name generic components by visual role: `Card`, `Badge`, `Button`.
- Name intelligence components by business presentation role: `MetricCard`.
- Name chart components by the data story they render: `RevenueChart`, `DiscountChart`.
- Keep page-specific orchestration in feature directories such as `chat/` and `dashboard/`.
- Prefer direct imports such as `@/components/ui/card` in new code. `@/components/ui` remains a compatibility barrel for existing consumers.
- Use semantic token utilities. Raw colors should be added only as tokens in `globals.css`, not embedded in component class names.

## Migration Notes

- Existing `Logo`, `Card`, `SectionLabel`, and `Spinner` exports remain available from `@/components/ui`.
- The chat and dashboard routes, API calls, loading behavior, and business content are unchanged.
- The legacy `AppHeader` remains available, but application pages now use `AppShell`.
- Dashboard metric and chart presentation moved out of the page composition module.
- Repeated dashed placeholders now use `EmptyState`.
- Dashboard and analyst content now use the wide workspace rather than centered `max-w-7xl` page containers.
- Future page work should use the shell context contract and add real navigation links only when routes exist.
