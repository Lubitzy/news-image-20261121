# Editorial notes — 21 November 2026

## Scope and method

- [evidence] The entry describes events in the Saturday 21 November edition. Its story data is a curated 15-item set spanning Europe, the Middle East, Asia, Oceania, the Americas and worldwide markets.
- [evidence] Each claim's source URLs, edition-derived wording, attribution and uncertainty are recorded in `stories.json`. The three lead stories follow the edition's own lead hierarchy. Other items are supporting panels or brief lines.
- [evidence] The text and claims were checked against `https://news.make.fun/2026-11-21.json` and the edition's Markdown page. The edition itself points to wire services, public agencies and named newsrooms. Individual links are included in the data for follow-up.
- [limitation] Some linked stories are attributed claims by a conflict party or public official; the wording retains that attribution or caveat. The compilation is not an exhaustive, independently fact-checked account of every event.
- [limitation] No direct visual service could inspect the render. A local Windows OCR pass and machine pixel/layout checks were used; unknown pictogram recognition remains unknown.

## Lead stories

1. **COP31 runs into Saturday without a deal.** AFP reported the Friday overtime, the draft's omission of fossil fuels and the continued lack of a political deal. The image says “COP31 overtime” and “no deal yet,” not that the summit ultimately failed. Source: AFP, 20 November, 20:42 UTC: https://www.afp.com/en/nations-row-over-fossil-fuels-cop31-goes-overtime
2. **Five missiles reportedly downed over Saudi Arabia.** The headline attributes the interception account to the Saudi-led coalition; it is not presented as independently verified imagery. The edition names AFP and Dawn; its linked follow-up is Arab News: https://www.arabnews.com/saudi-arabia/saudi-arabia-shoots-down-houthi-drones-and-missiles-3013163
3. **A magnitude 6.7 earthquake in central Peru.** The edition gives USGS and IGP; it notes no death reports and the deep quake. The illustration does not assert damage beyond the summarized report. Follow-up: https://www.riotimesonline.com/magnitude-6-7-earthquake-shakes-central-peru/

## Supporting panels and briefs

- Ukraine: Zelensky's warning about the Crimean Bridge is a quoted statement, not a claim that an event had already occurred. The edition links the Kyiv Independent via MSN.
- Iran: the asserted drone shootdown is qualified as Iran's claim, with no Washington confirmation in the summary.
- US data-centre policy: the threatened tax is a proposal/threat; the article says details were unspecified. AFP/The Hindu, published 21 November: https://www.thehindu.com/sci-tech/technology/trump-vows-to-punish-us-firms-building-data-centres-abroad/article71727296.ece
- China/Japan: Beijing's demand and Tokyo's unchanged-position response are described as statements.
- Aviation: the Air Niugini aircraft's safe landing is reported; no crash is implied.
- Markets: the Bitcoin price and 24-hour percentage are attributed to CoinGecko/Yahoo Finance in the feed.
- Australia/China AI talks, Formula 1, cricket, the EU's COP31 warning and the Roundup settlement are in the six short briefs. Wording distinguishes an agreement to talks, a practice result, an unfinished match, a warning and a court-approved settlement.

## Artwork and runtime

- [evidence] The artwork is authored vector-like geometry drawn locally; no photos, logos, downloaded fonts, maps or competitor assets are bundled.
- [evidence] `main.py` copies the frozen PNG byte-for-byte using only Python's standard library. All image-generation dependencies are build-time only.
- [assumption] The three lead panels are more important than the smaller secondary claims; they occupy larger cards by design.
- [limitation] This file is editorial provenance, not a claim of direct access to source articles where the edition supplies only a search link or a syndicated URL.
