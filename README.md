# ☕ Coffee Shopper — Live Listings

A single-page web app that aggregates **currently in-stock** coffees from
multiple specialty roasters and ranks every size option by **price per gram** —
the comparable unit price for deciding what to buy, *across roasters*.

**Roasters:**
- [Hydrangea Coffee Roasters](https://hydrangea.coffee)
- [Sey Coffee](https://seycoffee.com)
- [Black & White Roasters](https://www.blackwhiteroasters.com)

## Features
- **Live data, no backend.** Pulls each roaster's public Shopify catalog
  (`/products.json`, paginated) directly in the browser. Hit **Refresh** to
  re-pull; sold-out lots drop off and new ones appear. Fetches run in parallel
  and degrade gracefully if one roaster's site is unreachable.
- **Honest $/g.** Unit price uses the *actual roasted-coffee weight* (e.g.
  4 oz = 114 g, 250 g, 2 lb), not Shopify's shipping weight (which adds packaging).
- **Per-roaster filters** + colored badge on every listing, plus **Geisha-only**
  and **Washed-only** quick filters, text search, and sort.
- **Installable PWA.** "Add to Home Screen" gives a real app icon, fullscreen,
  works offline from the last cached pull.

## Data-quality note
Only **Hydrangea** publishes a structured varietal/origin/process. For **Sey**
and **Black & White**, those fields are parsed best-effort from the product
title and description (so some cells read "—"). Accordingly:
- **Washed-only** matches "washed" in the listing text for all roasters.
- **Geisha-only** uses Hydrangea's exact varietal field, and falls back to a
  "Gesha/Geisha" keyword match in the title/description for the others.
- **$/g, name, photo, sizes, prices** are reliable for all roasters — that's the
  core comparison.

## Adding another roaster
If it's a Shopify store (most specialty roasters are) with open CORS on
`/products.json`, add an entry to the `SOURCES` array in `index.html` and write
a small `parse*()` adapter that maps its products to the normalized record shape.
