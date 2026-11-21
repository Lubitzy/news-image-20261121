# Design review — 21 November 2026

## Candidate compositions

Three 1024×1024 compositions were rendered from the same 15 sourced claims:

- **A:** twelve equal cards, broad coverage but weak lead hierarchy.
- **B:** three large lead cards, six supporting panels and six attributed briefs.
- **C:** two large leads, eight narrower panels and five briefs.

## Selection

- [evidence] B gives the day's three lead topics the largest visual treatment while retaining 15 bounded claims.
- [evidence] The renderer completed all text-fit and body/source-clearance guards for A, B and C. B's rendered PNG is 391,055 bytes, within the 1 MiB artifact cap.
- [evidence] Native Windows OCR recovered B's date, all three lead headlines, supporting headlines and the brief lines at native size. OCR errors such as `A1` for `AI` and `IRE` for `IRIB` are retained as OCR limitations, not treated as artwork defects without visual confirmation.
- [evidence] At 300×300, OCR recovered the date and the three lead topics; small secondary copy is not claimed to be fully legible at that size.
- [limitation] The remote vision service denied this local image request. The assessment uses local OCR, exact text geometry and PNG/pixel checks; pictogram recognition remains unknown.

## Editorial hierarchy

B's three leads are COP31 overtime, the reported Saudi/Houthi missile interceptions and the Peru earthquake. Supporting panels cover conflict, diplomacy, technology, aviation and markets. The bottom brief strip adds Australia–China AI talks, Formula 1, cricket, the COP31 warning and the Roundup settlement without competing with the leads.

## Runtime and artifact

- [evidence] `main.py` imports only `argparse`, `pathlib` and `shutil`, and copies `assets/entry.png` without network, randomness, fonts or timestamps.
- [evidence] The committed artifact is an RGB, non-interlaced PNG at 1024×1024 and 391,055 bytes. The official standard-library verifier is run after the final copy.
- [evidence] The image contains original geometric illustrations and editorial text; no competitor artwork, news photograph, logo or downloaded font is distributed.
- [limitation] This is an editorial self-review, not a prediction of the sealed judge's visual preference or an official score.
