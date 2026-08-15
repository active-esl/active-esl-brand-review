# Integration contract — active-esl-brand-review

## Worktree layout

| Repo | Lane | Directory | Branch |
|------|------|-----------|--------|
| active-esl-brand-review | primary | `/data_drive/esl/active-esl-brand-review` | `main` (keep clean) |
| active-esl-brand-review | favicon | `/data_drive/esl/active-esl-brand-review-favicon` | `feat/edge-favicon` |
| active-esl-brand-review | email-strip | `/data_drive/esl/active-esl-brand-review-email-strip` | `feat/email-signature-strip-asset` |
| active-esl-brand-review | email-sig-publish | `/data_drive/esl/active-esl-brand-review-email-sig-publish` | `feat/cadence-stacked-lockup` |
| active-esl-brand-review | insights-refresh | `/data_drive/esl/active-esl-brand-review-insights-refresh` | `feat/active-edge-insights-refresh` |

## Review tip (Gary / Michael)

| Host | Role |
|------|------|
| `https://active-esl.com/` | Production — GitHub Pages from `main` |
| `https://review.active-esl.com/` | Stakeholder review — Cloudflare Worker `active-esl-website-review` from the `review` branch tip |

Deploy review: `./scripts/deploy-review.sh` (requires `ACTIVE_ESL_CLOUDFLARE_API_TOKEN`).
Hostname-gated banner in `assets/js/site.js` marks the review tip.
