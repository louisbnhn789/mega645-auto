# Mega 6/45 – Historical analysis dashboard
Runs at 20:30 and 22:30 Vietnam time via GitHub Actions (subject to GitHub delays).

**Setup:** Settings → Pages → Deploy from a branch → main /docs; Settings → Actions → General → Workflow permissions → Read and write. Optionally set Actions variable MEGA645_CSV_URL to a trustworthy direct CSV URL with fields product,draw_status,draw_id,draw_date,result_json. Without a fresh source, results remain stale and the page warns you.

Run manually: Actions → Mega645 Auto Update → Run workflow.

Historical rankings are not validated probabilities of winning. A fair Mega 6/45 draw gives each 6-number combination the same jackpot probability.

## Sources
- Archived full history: NhanAZ-Data/vietlott-data-research (ends July 2026)
- Updated NDJSON: https://github.com/vietvudanh/vietlott-data/blob/main/data/power645.jsonl

The updater merges by date and six-number set and rejects conflicting records. If the upstream feed fails, it uses the last successfully saved copy and displays staleness. The GitHub workflow must be run once after this change to publish updated results.
