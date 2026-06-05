---
name: Deep Growth Horizon
colors:
  surface: '#101417'
  surface-dim: '#101417'
  surface-bright: '#36393d'
  surface-container-lowest: '#0b0e12'
  surface-container-low: '#191c1f'
  surface-container: '#1d2023'
  surface-container-high: '#272a2e'
  surface-container-highest: '#323539'
  on-surface: '#e1e2e7'
  on-surface-variant: '#bacac1'
  inverse-surface: '#e1e2e7'
  inverse-on-surface: '#2e3134'
  outline: '#85948c'
  outline-variant: '#3c4a43'
  surface-tint: '#2fe0aa'
  primary: '#44edb7'
  on-primary: '#003828'
  primary-container: '#00d09c'
  on-primary-container: '#00533c'
  inverse-primary: '#006c4f'
  secondary: '#c8c6c5'
  on-secondary: '#313030'
  secondary-container: '#4a4949'
  on-secondary-container: '#bab8b7'
  tertiary: '#ced3de'
  on-tertiary: '#2b3139'
  tertiary-container: '#b2b8c2'
  on-tertiary-container: '#434952'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#59fdc5'
  primary-fixed-dim: '#2fe0aa'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513b'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1c1b1b'
  on-secondary-fixed-variant: '#474646'
  tertiary-fixed: '#dde3ee'
  tertiary-fixed-dim: '#c1c7d1'
  on-tertiary-fixed: '#161c24'
  on-tertiary-fixed-variant: '#414750'
  background: '#101417'
  on-background: '#e1e2e7'
  surface-variant: '#323539'
typography:
  headline-lg:
    fontFamily: Manrope
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-md:
    fontFamily: Manrope
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Manrope
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Manrope
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 32px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base-unit: 4px
  gutter: 24px
  margin-desktop: 64px
  margin-mobile: 16px
  container-max-width: 1200px
---

## Brand & Style

The design system is engineered for a sophisticated, high-trust investment environment. It utilizes a **Corporate Modern** aesthetic with a heavy emphasis on **Dark Mode** to reduce eye strain during long analytical sessions. The personality is optimistic yet grounded, characterized by the vibrant "Groww Green" which symbolizes prosperity and vitality against a deep, stable background. 

The visual language focuses on high-contrast information density. Key attributes include:
- **Clarity & Precision:** Using a strict grid and clear typography to make complex financial data digestible.
- **Trust-Oriented:** A clean, professional look that avoids unnecessary flourishes, focusing instead on structural integrity and data accuracy.
- **AI-Enhanced:** A seamless integration of conversational interfaces that feel like a natural extension of the platform rather than an add-on.

## Colors

The palette is optimized for a deep-theme experience where contrast is used to define hierarchy.

- **Primary (Groww Green):** Used for primary actions, success states, positive growth trends, and AI assistant accents.
- **Background (Secondary):** A true deep dark (#121212) for the main canvas to ensure content pops.
- **Surface (Tertiary):** A slightly lighter shade (#232931) for cards, headers, and container elements to create depth.
- **Interaction (Neutral):** Subdued greys for borders, secondary text, and inactive states.
- **Semantic Colors:** Soft reds are reserved for negative trends, while the primary green remains the dominant indicator of performance.

## Typography

This design system uses a dual-font approach. **Manrope** is used for headlines to provide a modern, geometric, and trustworthy feel. **Inter** is used for all functional text, data points, and UI labels due to its exceptional legibility at small sizes and neutral, systematic character.

Numbers and financial figures should always be rendered in Inter with tabular lining to ensure vertical alignment in lists and tables. Bold weights are used sparingly to highlight key performance indicators (KPIs).

## Layout & Spacing

The layout follows a **Fixed Grid** system for desktop to maintain optimal readability of financial charts and tables, while transitioning to a **Fluid Grid** for mobile devices.

- **Grid:** A 12-column grid for desktop with 24px gutters. 
- **AI Sidebar:** On wide screens, the AI Assistant and Chat History occupy a fixed 320px right-aligned panel. On mobile, this transforms into a full-screen modal or a bottom-sheet.
- **Rhythm:** An 8px spacing scale is used for component-level layout, while 4px increments are used for internal component padding to maintain high information density without feeling cluttered.

## Elevation & Depth

Depth in this design system is created through **Tonal Layers** rather than heavy shadows. 

- **Level 0 (Background):** Primary canvas at #121212.
- **Level 1 (Cards/Containers):** Surfaces at #232931 with a subtle 1px border (#44474B) to define edges against the dark background.
- **Level 2 (Modals/Overlays):** Elevated surfaces that use a slightly lighter grey and a very soft, diffused ambient shadow (0px 8px 24px rgba(0,0,0,0.5)) to suggest floating.
- **AI Components:** The AI chat bubbles use tonal differentiation—user messages are Primary Green, while assistant responses are Surface Grey to maintain clear conversational flow.

## Shapes

The shape language is **Rounded**, strike a balance between the precision of finance and the approachability of a modern tech product.

- **Standard Elements:** Buttons, inputs, and small cards use a 0.5rem (8px) radius.
- **Large Containers:** Main dashboard cards and the AI Assistant panel use a 1rem (16px) radius to soften the high-contrast interface.
- **Interactive Icons:** Circular containers (pill-shaped) are used for feature badges (e.g., "NEW") and user profile avatars.

## Components

### Buttons & Inputs
- **Primary Button:** Solid Groww Green background with black text for maximum contrast.
- **Secondary Button:** Ghost style with a Groww Green border and text.
- **Input Fields:** Dark background (#121212) with a subtle border that glows Primary Green on focus.

### Cards
- **Investment Cards:** Feature a high-contrast layout. Title and main value are prominent, with sub-data (e.g., 3Y returns) in a smaller, muted label style. 
- **AI Chat Interface:** Messages are housed in containers with 12px padding. The input area for the AI assistant is a prominent, full-width text area at the bottom of the sidebar with a "Spark" icon to denote AI capability.

### Navigation & Tags
- **Tabs:** Underline style using the Primary Green for the active state.
- **Chips:** Small, pill-shaped badges for categories (e.g., "Equity," "Debt") or status indicators (e.g., "Open," "Live") using low-opacity versions of semantic colors.
- **Chat History Sidebar:** A vertical list of previous queries with a hover state that lightens the background slightly to #2D343E.