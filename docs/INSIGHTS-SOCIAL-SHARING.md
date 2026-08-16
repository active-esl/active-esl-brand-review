# Insights social-sharing contract

Checked: 2026-08-15

Each Insight is a stable, independently shareable page under
`https://active-esl.com/insights/`. The page owns the title, summary, preview
image and structured data that social networks and search engines should use.

## LinkedIn archive adaptations

When an Insight is adapted from Alex's earlier LinkedIn writing:

- show **Originally published on LinkedIn** with the exact source date and link
- use that original date as `datePublished`
- show the current website adaptation date and use it as `dateModified`
- preserve the substance and Alex's first-person stake while restructuring for
  durable long-form reading
- do not imply the Active-Edge website hosted the article on the original date

## Link-preview image

- Exact export: **1200 × 627 px** (1.91:1), PNG, sRGB, under 5 MB.
- Keep the headline legible at feed-card size and important content away from
  the outer edge.
- Use the current **Active-Edge** name and brand tokens.
- Store in `assets/images/insights/` and render from
  `scripts/render_insight_social_cards.py`.
- A portrait 1080 × 1350 image may still accompany an image-led LinkedIn post,
  but it is not the Open Graph link-preview asset.

Sources:

- Official LinkedIn Help:
  [Make your website shareable on LinkedIn](https://www.linkedin.com/help/linkedin/answer/a521928)
  — 1200 × 627 minimum, 1.91:1 recommended, maximum 5 MB.
- Common current guide:
  [Hootsuite social-media image sizes](https://blog.hootsuite.com/social-media-image-sizes-guide/)
  — 1200 × 627 for a LinkedIn post with URL.

## Required page metadata

- canonical production URL
- `og:type=article`, `og:url`, `og:title`, `og:description`
- `og:image` plus secure URL, MIME type, width, height and accessible alt text
- publication and modification dates, author, section and tags
- `twitter:card=summary_large_image` and matching image alt
- `robots=index,follow,max-image-preview:large`
- `BlogPosting` JSON-LD with URL, dates, language, author, publisher and an
  `ImageObject` carrying 1200 × 627 dimensions

## Share controls

Every article footer includes:

- **Share on LinkedIn** using LinkedIn's off-site share endpoint with the
  canonical production URL
- **Copy link** with an accessible live-region confirmation

The LinkedIn composer supplies the user's post text. Do not prefill it: the
preview title, summary and image come from the article metadata.

## Publish check

1. Render cards: `python3 scripts/render_insight_social_cards.py`.
2. Confirm each PNG is exactly 1200 × 627 and below 5 MB.
3. Validate HTML and JSON-LD locally.
4. Deploy the stakeholder review tip and check page/share-control layout.
5. After production publication, submit each canonical URL to
   [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/) to refresh
   LinkedIn's cached preview and confirm the final card.
