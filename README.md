# ☕ Hydrangea Coffee — Live Listings

A single-page web app that shows every **currently in-stock** coffee from
[Hydrangea Coffee Roasters](https://hydrangea.coffee), with each size option's
**price per gram** — the comparable unit price for deciding what to buy.

- **Live data.** Pulls the roaster's public Shopify catalog
  (`hydrangea.coffee/products.json`) directly in the browser. Hit **Refresh** to
  re-pull anytime; sold-out lots drop off and new ones appear automatically.
- **Honest $/g.** Unit price is computed from the *actual roasted-coffee weight*
  (e.g. 4 oz = 114 g), not Shopify's shipping weight (which includes ~20 g of
  packaging).
- **Installable.** It's a PWA — open it on a phone and "Add to Home Screen" for a
  real app icon that opens fullscreen.
- **No backend.** Just static files (`index.html`, `manifest.webmanifest`,
  `sw.js`, `icons/`). Works offline from the last cached pull.

Pulls in-stock products of type `Coffee` / `Rested Coffee`, parses varietal /
farm / origin / process from each product description, and ranks by $/g.
