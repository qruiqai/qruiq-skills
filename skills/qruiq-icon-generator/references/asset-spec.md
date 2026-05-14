# Asset spec

Every file the skill produces, what it's for, and where it gets referenced.

## Master and favicons (output dir = auto-detected `public/`, `static/`, etc.)

| File | Size | Purpose | Referenced by |
|---|---|---|---|
| `icon.png` | 1024×1024 | Master copy. Useful for README badges, link previews, anywhere you need a hi-res version. | none by default — it's a reusable artifact |
| `favicon.ico` | multi (16/32/48) | Legacy favicon. IE, older browsers, default fallback. | `<link rel="icon" type="image/x-icon" href="favicon.ico">` |
| `favicon-16x16.png` | 16×16 | Browser tab favicon, small. | `<link rel="icon" sizes="16x16">` |
| `favicon-32x32.png` | 32×32 | Browser tab favicon, default. Also used for bookmarks. | `<link rel="icon" sizes="32x32">` |
| `apple-touch-icon.png` | 180×180 | iOS home-screen icon when "Add to Home Screen". | `<link rel="apple-touch-icon">` |
| `android-chrome-192x192.png` | 192×192 | Android home-screen icon (manifest reference). | `site.webmanifest` |
| `android-chrome-512x512.png` | 512×512 | Android splash + high-res home screen. | `site.webmanifest` |
| `og-image.png` | 1200×630 | Social media link preview (Twitter/X, Slack, Discord, Facebook, LinkedIn). | `<meta property="og:image">`, `<meta name="twitter:image">` |

## Manifest

| File | Purpose |
|---|---|
| `site.webmanifest` | PWA manifest. Tells browsers/OSes the app's name, theme color, and which icons to use for home-screen install. Even non-PWAs benefit — Chrome uses it for the install prompt and macOS Safari uses it for pinned tabs. |

## HTML head snippet

The skill prints a snippet for the user to paste into their root layout
(`<head>`). The snippet covers:

- Three `<link rel="icon">` tags (ICO + 16×16 PNG + 32×32 PNG) — browsers pick
  the most appropriate
- `<link rel="apple-touch-icon">` for iOS
- `<link rel="manifest">` for the webmanifest
- `<meta name="theme-color">` for mobile browser chrome color
- Open Graph + Twitter card meta tags for `og-image.png`

## Notes

- **`{{BASE_PATH}}`** in the snippet/manifest is empty (`""`) for sites served
  from a domain root, or `"/subpath/"` for sites served from a subpath. Default
  to empty if you can't tell.
- **`apple-touch-icon-precomposed.png`** used to be required separately. iOS
  has automatically composed for years; we don't emit a separate file.
- **`safari-pinned-tab.svg`** would require a vector SVG. We don't emit one
  because the image model produces raster output. Skip it; the .ico fallback
  handles Safari just fine.
- **Don't compress these aggressively.** Pillow's `optimize=True` is enough.
  Running them through tinypng often adds banding to flat icons and the
  byte savings on a 16×16 PNG are pointless.
