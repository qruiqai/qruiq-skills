# Prompt guide: how to brief the image model

Image generation models are good at executing on a clear, opinionated brief and bad at filling in vague gaps. The job here is to translate what you learned about the project into a brief that produces an icon that survives at 16×16.

## The template

```
A {{STYLE}} icon for {{NAME}}, {{ONE_LINE_PURPOSE}}.

Subject: {{SINGLE_FOCAL_SUBJECT}}.
Composition: centered in a square frame, generous negative space, balanced.
Color: {{PALETTE_OR_BRAND_COLOR}}.
Background: pure white (#FFFFFF), no transparency, no checker pattern, no gradient — the asset script keys it to alpha after generation.
Constraints: no text, no letters, no logos of other brands; flat or low-detail
so it stays readable when shrunk to 16×16; high contrast between the subject
and the background; no photorealism, no skeuomorphism, no cluttered backgrounds.
```

Fill the slots from what you extracted in the project-reading step. If a slot
is genuinely unknown after reading the project, ask the user — don't guess.

## Why each constraint matters

- **Always ask for solid white background, not transparent.** Image models
  (including `gpt-5.4-image-2`) treat "transparent background" as an
  instruction to literally paint a transparency-checker pattern as opaque
  pixels — you end up with a baked-in checker around the icon. Asking for a
  flat white background is reliable, and `make_assets.py` strips the white to
  real alpha via saturation-based keying. The icon's brand color must be
  something other than pure white for the keying to work — but a pure-white
  icon is a bad choice anyway.
- **Single focal subject.** Two subjects compete at small sizes and turn into
  visual noise. One strong shape per icon.
- **Generous negative space.** Browsers and OSes crop favicons unpredictably
  (rounded corners, masks, square tiles). Padding gives the icon room to breathe
  and survive these crops.
- **No text, no letters, no logos of other brands.** Image models render text
  poorly, especially at small sizes. The project name lives in the `<title>`
  tag and the OG card — never inside the icon itself. "No logos of other
  brands" prevents accidentally generating a knockoff (a generic "github octopus"
  shape, etc.) when the model reaches for visual shorthand.
- **Flat or low-detail.** Detail dies below 32×32. Flat illustration, line art,
  or simple gradients survive. Highly detailed illustration or photoreal
  rendering becomes mush.
- **High contrast between subject and background.** Browser tabs are tiny.
  Without strong contrast, the icon disappears.
- **No photorealism, no skeuomorphism.** These styles look fine at hero size
  and terrible at favicon size. Icons live at favicon size 99% of the time.

## Style anchors that work

If the user didn't pick a style and you couldn't extract one from the project,
these are reliable defaults — pick the one that best matches the project's tone:

- **"minimalist line art with a 4px stroke, two-color"** — for technical /
  developer tools / clean SaaS
- **"flat geometric, 2-3 color palette"** — for productivity / consumer apps
- **"glyph mark on a solid rounded-square tile, single accent color"** —
  app-icon style; works well for mobile-flavored projects
- **"abstract emblem in a single bold color on transparent"** — for libraries
  or open-source tools where the brand is the abstraction itself

## What "AI slop" looks like (avoid)

If your generated icon has any of these, it's a slop tell — not 90+ material:

- Random extra elements floating in the background ("decorative" sparkles,
  swooshes, light rays)
- Lopsided symmetry — a shape that looks symmetric at first glance but isn't
  on closer inspection
- Weirdly textured edges from over-rendered "3D" effects
- Half-rendered text (the model tried to write the name and gave up)
- Generic "tech" imagery: circuit boards, glowing nodes, neural-net diagrams,
  abstract chrome shapes

When you see these in the output, name them in the critique and rewrite the
prompt to explicitly forbid them in the next iteration.

## Example brief

For a project named "Lumen" described as "a fast file watcher that streams
build events to your editor":

> A minimalist line-art icon for Lumen, a fast file watcher that streams build
> events to a code editor. Subject: a stylized lighthouse beam — a single beam
> of light radiating out from a small geometric source point — rendered as
> clean two-tone line art. Composition: centered in a square frame, generous
> negative space, balanced. Color: deep indigo (#3730A3) lines on transparent
> background. Constraints: no text, no letters, no logos of other brands; flat
> low-detail so it stays readable at 16×16; high contrast; no photorealism, no
> skeuomorphism, no cluttered backgrounds.

This brief is doing real work: a metaphor (lighthouse = watching, beam =
streaming), a style commitment (line art), a color commitment (indigo), and
a list of failure modes to avoid. That's the bar for a first prompt.
