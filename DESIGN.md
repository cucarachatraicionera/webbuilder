---
name: Exercise
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#393939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1b1b1b'
  surface-container: '#1f1f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353535'
  on-surface: '#e2e2e2'
  on-surface-variant: '#e3bfb1'
  inverse-surface: '#e2e2e2'
  inverse-on-surface: '#303030'
  outline: '#aa8a7d'
  outline-variant: '#5a4136'
  surface-tint: '#ffb596'
  primary: '#ffb596'
  on-primary: '#581e00'
  primary-container: '#ff6600'
  on-primary-container: '#561d00'
  inverse-primary: '#a33e00'
  secondary: '#c8c6c5'
  on-secondary: '#313030'
  secondary-container: '#474746'
  on-secondary-container: '#b7b5b4'
  tertiary: '#c8c6c5'
  on-tertiary: '#303030'
  tertiary-container: '#989696'
  on-tertiary-container: '#2f2f2f'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdbcd'
  primary-fixed-dim: '#ffb596'
  on-primary-fixed: '#360f00'
  on-primary-fixed-variant: '#7c2e00'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1c1b1b'
  on-secondary-fixed-variant: '#474746'
  tertiary-fixed: '#e4e2e1'
  tertiary-fixed-dim: '#c8c6c5'
  on-tertiary-fixed: '#1b1c1c'
  on-tertiary-fixed-variant: '#474746'
  background: '#131313'
  on-background: '#e2e2e2'
  surface-variant: '#353535'
typography:
  display-xl:
    fontFamily: Montserrat
    fontSize: 80px
    fontWeight: '900'
    lineHeight: '1.0'
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Montserrat
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Montserrat
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-bold:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '700'
    lineHeight: '1.2'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 48px
  grid-margin: 24px
  grid-gutter: 16px
---

## Brand & Style

This design system is engineered for high-performance environments where speed, clarity, and intensity are paramount. The aesthetic is rooted in **High-Contrast Boldness**, stripping away decorative elements to focus on raw utility and visual impact. It targets serious athletes and performance-driven individuals who value results over aesthetics.

The visual language communicates a "No excuses" mentality through heavy typography and a restricted, high-energy color palette. Surfaces are dark and imposing, ensuring that the primary brand color cuts through the interface with maximum luminance. Every element is designed to feel heavy, industrial, and unyielding.

## Colors

The color strategy for this design system is strictly high-contrast to facilitate readability in low-light gym environments.

- **Primary:** Vibrant Orange (#FF6600) is used exclusively for primary actions, progress indicators, and critical performance data.
- **Surface Tiers:** The foundation is absolute Black (#000000). Secondary surfaces use Deep Charcoal (#1A1A1A) to create subtle separation without losing the aggressive dark aesthetic.
- **Accents:** A tertiary Grey (#262626) provides depth for borders and inactive states. 
- **Feedback:** Use pure White (#FFFFFF) for maximum legibility on text and Pure Red for error states to maintain the aggressive tone.

## Typography

Typography is used as a structural element. Headlines are set in **Montserrat** with heavy weights (ExtraBold/Black) to command attention and instill a sense of power. Use uppercase for primary headlines and call-outs to reinforce the aggressive brand voice.

Body text utilizes **Inter** for its exceptional clarity and technical feel. Line heights are kept tight for headings to maximize density, while body text is given generous leading to ensure athletes can read instructions or data quickly during high-intensity intervals. All labels and secondary metadata should be set in uppercase with slight tracking increases for a "tactical" appearance.

## Layout & Spacing

This design system employs a **fixed-column grid** (12 columns for desktop, 4 for mobile) with a strict 4px baseline. The spacing rhythm is aggressive and compact, favoring density of information over excessive whitespace.

Margins are kept wide (24px+) to frame the content, while gutters remain tight (16px) to keep related data points physically close. Alignment should be rigid and predominantly left-aligned or centered for display moments; avoid staggered or organic layouts.

## Elevation & Depth

In this design system, depth is achieved through **Tonal Layering** rather than shadows. Shadows are largely avoided to maintain a flat, industrial aesthetic. 

Higher-level components (like cards or modals) are elevated by using slightly lighter charcoal shades (e.g., #1A1A1A against #000000). To indicate focus or interactivity, use 1px solid borders in the primary orange or tertiary grey. When a shadow is absolutely necessary for accessibility, use a "Hard Shadow" — a zero-blur, high-opacity offset that mimics a physical extrusion.

## Shapes

The shape language is sharp and precise. A standard corner radius of **4px (Soft)** is applied to buttons, input fields, and containers to prevent the interface from feeling brittle while maintaining a modern, aggressive edge. 

- Icons should feature 90-degree angles or minimal rounding.
- Progress bars and data visualizations must use square caps rather than rounded ones.
- Interactive triggers should feel "cut" and architectural.

## Components

- **Buttons:** Primary buttons feature a solid #FF6600 background with Black text, using the `label-bold` style. Hover states should invert to a white border with orange text. Secondary buttons are "Ghost" style with white borders and no fill.
- **Cards:** Backgrounds use #1A1A1A with no shadow. Use a 1px #262626 border for definition. For high-priority cards (e.g., "Workout Active"), use a 4px left-hand border in #FF6600.
- **Inputs:** Dark backgrounds (#000000) with a 1px #262626 bottom border only. On focus, the border transitions to #FF6600. 
- **Chips/Badges:** Small, rectangular, and set in uppercase. Use high-contrast backgrounds (White or Orange) to denote status.
- **Lists:** Clean, strictly horizontal separators using 1px #262626. Use Montserrat for list item titles to maintain the bold character.
- **Performance Gauges:** Use heavy stroke weights (8px+) for ring charts and bars. No gradients; use solid #FF6600 against #262626 backgrounds for a digital-industrial look.