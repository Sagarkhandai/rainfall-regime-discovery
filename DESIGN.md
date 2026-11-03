---
name: Rainfall Atlas
colors:
  surface: '#0a1422'
  surface-dim: '#0a1422'
  surface-bright: '#303a49'
  surface-container-lowest: '#050e1c'
  surface-container-low: '#121c2a'
  surface-container: '#16202f'
  surface-container-high: '#212a39'
  surface-container-highest: '#2c3545'
  on-surface: '#d9e3f7'
  on-surface-variant: '#bcc9cb'
  inverse-surface: '#d9e3f7'
  inverse-on-surface: '#273140'
  outline: '#869395'
  outline-variant: '#3d494b'
  surface-tint: '#56d7e9'
  primary: '#8ff0ff'
  on-primary: '#00363d'
  primary-container: '#54d6e8'
  on-primary-container: '#005a64'
  inverse-primary: '#006874'
  secondary: '#5cdac9'
  on-secondary: '#003731'
  secondary-container: '#04a596'
  on-secondary-container: '#00332d'
  tertiary: '#a2edfa'
  on-tertiary: '#00363d'
  tertiary-container: '#86d1dd'
  on-tertiary-container: '#005b64'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#95f1ff'
  primary-fixed-dim: '#56d7e9'
  on-primary-fixed: '#001f24'
  on-primary-fixed-variant: '#004f57'
  secondary-fixed: '#7bf7e5'
  secondary-fixed-dim: '#5cdac9'
  on-secondary-fixed: '#00201c'
  on-secondary-fixed-variant: '#005048'
  tertiary-fixed: '#a3effb'
  tertiary-fixed-dim: '#87d2de'
  on-tertiary-fixed: '#001f24'
  on-tertiary-fixed-variant: '#004f57'
  background: '#0a1422'
  on-background: '#d9e3f7'
  surface-variant: '#2c3545'
typography:
  display:
    fontFamily: Space Grotesk
    fontSize: 56px
    fontWeight: '600'
    lineHeight: 64px
    letterSpacing: -0.03em
  display-mobile:
    fontFamily: Space Grotesk
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-xl:
    fontFamily: Space Grotesk
    fontSize: 40px
    fontWeight: '500'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Space Grotesk
    fontSize: 28px
    fontWeight: '500'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '500'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
    letterSpacing: 0em
  body-lg:
    fontFamily: Manrope
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Manrope
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-sm:
    fontFamily: Manrope
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0.005em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.04em
  code-metric:
    fontFamily: JetBrains Mono
    fontSize: 22px
    fontWeight: '500'
    lineHeight: 26px
    letterSpacing: -0.02em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-sm: 0.75rem
  gutter-lg: 2rem
  margin: 2rem
  margin-mobile: 1rem
  margin-desktop: 3rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system embodies the rigor of climate intelligence, oceanic atmospheric modeling, and editorial scientific discovery. Designed for meteorologists, environmental researchers, enterprise risk modelers, and institutional policymakers, the UI conveys unquestioned authority, surgical precision, and natural elegance.

The visual direction marries **Apple-inspired precision minimalism** with **restrained glassmorphic depth**. Surfaces emulate deep ocean layers and atmospheric strata: ultra-deep oceanic ink backdrops, subtle optical glass sheets, hairline borders with controlled luminance, and sharp, technical data readouts. Interactions should feel frictionless, weighted, and calm—evoking the quiet scale of planetary weather systems translated into pristine, intelligible instruments.

## Colors

The palette draws inspiration from abyssal waters, dense rain clouds, and glowing scientific instruments:

- **Primary (`#54D6E8` - Luminous Cyan):** The core atmospheric focal point. Used for critical vectors, current regime isolines, high-probability precipitation paths, active tabs, and primary interactive states.
- **Secondary (`#3BBFAF` - Ocean Turquoise):** Represents positive anomalies, moisture saturation layers, corroborating trend lines, and secondary confirmation states.
- **Tertiary (`#91DCE8` - Glacier Blue):** Applied to subtle highlight metrics, technical accents, radar overlays, and tertiary status tags.
- **Supportive Accents:**
  - *Muted Emerald (`#2E8B73` / `#1F5A4D`):* Normal rainfall stability, baseline vegetative index, standard regime health.
  - *Silver Mist (`#CAD7E3` / `#8B9DAE`):* Structural captions, metadata legends, coordinate grids, and neutral telemetry points.
- **Atmospheric Neutrals (Surface Layering):**
  - *Canvas Abyssal (`#07111F`):* Deepest background substrate.
  - *Stratum Deep (`#0A1928`):* Primary structural containers, side docks, and map canvas overlays.
  - *Stratum Elevated (`#102334`):* Floating instrument panels, analysis cards, inspect flyouts, and modal viewports.
  - *Stratum Bright (`#173248`):* Hover states, interactive wells, and elevated telemetry surfaces.
- **Border Channels:** Use hairline 1px strokes with variable alpha channel opacity (`rgba(84, 214, 232, 0.12)` down to `rgba(255, 255, 255, 0.06)`).

## Typography

Typography establishes an editorial and analytical cadence. 

- **Space Grotesk (Display & Headlines):** Imparts clean, contemporary geometric structure with subtle technical character. Headings must always maintain tight negative tracking to avoid loose visual tension.
- **Manrope (Body & Narrative):** Provides balanced humanist legibility for dense climate summaries, pattern methodology notes, and longitudinal reports.
- **JetBrains Mono (Telemetry, Metadata & Readouts):** Anchor for numerical metrics, geocoordinates, millibar values, date ranges, and standard deviation intervals. Sets tabular numbers (`tnum`) by default to prevent visual jitter across updating real-time feeds.

## Layout & Spacing

Layouts follow an asymmetric 12-column fluid workbench architecture designed for high-density spatial viewing:

- **Desktop (1440px+):** 12 columns with 24px (`1.5rem`) gutters and 48px (`3rem`) page boundaries. Primary viewport integrates a split dynamic canvas: a dedicated 8-column historical map/cartographic exploration field paired with a 4-column persistent regime inspector.
- **Tablet (768px - 1439px):** 8 columns with 16px (`1rem`) gutters. The inspector converts to a docked bottom slide-up tray or tabbed view.
- **Mobile (< 768px):** 4 columns with 12px (`0.75rem`) gutters and 16px (`1rem`) lateral margins. Map and data cards stack sequentially with fixed floating pill-switch controls.

Spacing scale strictly manages spatial distribution:
- `space-xs` (4px) and `space-sm` (8px) govern micro-alignments in numerical badges, data tags, and icon-to-label offsets.
- `space-md` (16px) defines internal padding for metric chips, dropdown panels, and cell separations.
- `space-lg` (24px) establishes internal padding for primary instrumentation tiles and analysis panels.
- `space-xl` (40px) controls section hierarchy and analytical module division.

## Elevation & Depth

Visual hierarchy uses restrained atmospheric stratification:

1. **Substrate (Base Level):** Raw canvas `#07111F` containing the raster tiles, map terrain, or bathymetric rainfall projections.
2. **Glassmorphic Paneling (Level 1):** Color `#0A1928` with 72% opacity (`rgba(10, 25, 40, 0.72)`), paired with `backdrop-filter: blur(20px) saturate(180%)`. Outlined with a fine 1px stroke of `rgba(255, 255, 255, 0.08)` on top and `rgba(84, 214, 232, 0.05)` on bottom to suggest top-down directional ambient lighting.
3. **Elevated Floating Instruments (Level 2):** Color `#102334` at 88% opacity, `backdrop-filter: blur(32px)`. Outlined with 1px stroke of `rgba(84, 214, 232, 0.22)`. Ambient shadow: `0 12px 32px -4px rgba(2, 6, 12, 0.65), 0 0 1px 1px rgba(84, 214, 232, 0.1)`.
4. **Active Focus & Modals (Level 3):** Solid `#102334` surrounded by an atmospheric cyan-tinted aura: `0 20px 48px -8px rgba(0, 0, 0, 0.8), 0 0 24px -2px rgba(84, 214, 232, 0.25)`.

No heavy cast drop shadows are permitted without luminous color dampening.

## Shapes

The design system employs a **Soft** shape geometry (`roundedness: 1`):
- Base interactive elements (buttons, inputs, telemetry badges): `0.25rem` (4px).
- Structural analytics cards, panels, and floating monitors: `rounded-lg` at `0.5rem` (8px).
- Modals, large spatial toolboxes, and drawer views: `rounded-xl` at `0.75rem` (12px).
- Micro regime indicators, status lights, and coordinate coordinate pins: full circular radius (`9999px`).

This restrained corner radius preserves architectural sharpness, avoiding playfulness and projecting instrument-grade calibration.

## Components

### Buttons
- **Primary Action:** Solid background of `#54D6E8` with `#07111F` text in `label-md` weight. Hover: transitions to `#91DCE8` with an external glow of `0 0 16px rgba(84, 214, 232, 0.4)`. Fine border is omitted on primary solid actions.
- **Secondary/Ghost Action:** Background `rgba(16, 35, 52, 0.6)`, text `#CAD7E3`, 1px border of `rgba(84, 214, 232, 0.2)`. Hover: border brightens to `#54D6E8`, text shifts to pure white `#FFFFFF`.

### Chips & Telemetry Badges
- Compact indicators containing an icon, value, and unit readout.
- Background: `rgba(10, 25, 40, 0.65)` with 1px border in `rgba(255, 255, 255, 0.08)`.
- Active regime chip uses a 4px turquoise or cyan luminous dot alongside `label-sm` monospace text.

### Input Fields & Selectors
- Background: `rgba(7, 17, 31, 0.8)`, border: 1px `rgba(255, 255, 255, 0.12)`.
- Text: Manrope body styling in silver `#CAD7E3`.
- Focus state: Border shifts to `#54D6E8` with a subtle 2px blur halo `rgba(84, 214, 232, 0.2)`.

### Cards & Analytical Panels
- Composed of translucent `Stratum Deep` (`rgba(10, 25, 40, 0.75)`) with backdrop blur.
- Cards feature an upper 1px hairline border at `rgba(255, 255, 255, 0.12)` fading to `rgba(255, 255, 255, 0.02)` at the baseline.
- Titles formatted in `headline-sm` Space Grotesk; sub-readouts formatted in `JetBrains Mono`.

### Specialized Domain Components
- **Isohyet Legend (Precipitation Band Bar):** Segmented color ramp starting from abyssal translucent blue (`0mm`) through Glacier Blue (`50mm`), Luminous Cyan (`150mm`), and Turquoise (`300mm+`), overlaid with hairline ticks and numerical value readouts in `label-sm`.
- **Temporal Epoch Scrubber:** A timeline slider with 1px glass rails, showing historical anomaly flags as 2px luminous ticks, with a draggable glacier-cyan thumb displaying year and deviation values dynamically.
- **Regime Anomaly Matrix:** Multi-column compact list with alternating rows (`rgba(255, 255, 255, 0.02)`), tabular alignment, and +/- variance indicators styled in Turquoise (`#3BBFAF`) or Amber Alert (`#E5A93C`).