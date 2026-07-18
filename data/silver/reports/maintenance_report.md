# Maintenance Report

Generated at: `2026-07-17T15:05:51.575672+00:00`

## Inputs

- Pages: `data/silver/datasets/rag_pages.csv`
- Links: `data/silver/datasets/rag_links.csv`
- Chunks: `data/silver/datasets/rag_chunks.csv`

## Counts

- Pages: 490
- Links: 22548
- Chunks: 4239

## Source Freshness

- Page retrieval window: `2026-06-24T07:40:10+00:00` to `2026-06-24T07:40:10+00:00`
- Chunk retrieval window: `2026-06-21T19:13:49+00:00` to `2026-06-24T07:40:10+00:00`
- Pages missing source-updated date: 44
- Chunks missing source-updated date: 287
- Chunks with freshness score below 0.5: 1517

Drift status counts:
- `changed`: 121
- `fetch_failed`: 4
- `new`: 4
- `unchanged`: 361

## Broken Link And Fetch Output

- Non-200 pages: 4
- Fetch-failed pages: 4
- Pages with fetch errors: 4
- Not-crawled links: 22079

Skip reason counts:
- `<blank>`: 469
- `contact_link`: 102
- `depth_limit`: 3016
- `duplicate_url`: 7281
- `email_like_url`: 12
- `external_domain`: 2576
- `file_or_pdf`: 192
- `max_pages_from_seed_reached`: 762
- `outside_allowed_path`: 7909
- `per_page_link_limit`: 228
- `unsupported_scheme`: 1

## Missing Data Output

- Missing page columns: none
- Missing link columns: none
- Missing chunk columns: none
- Blank page values: {'source_updated_at': 44}
- Blank link values: none
- Blank chunk values: {'source_updated_at': 287}

## Category Coverage Output

- Observed categories: 11
- Missing categories: ['safety_urgent']
- Low chunk coverage categories: ['language_integration', 'safety_urgent']

Chunk counts by category:
- `academics`: 199
- `documents_admin`: 55
- `finances`: 657
- `health_care`: 350
- `housing`: 88
- `immigration_status`: 402
- `insurance`: 90
- `language_integration`: 2
- `mental_health`: 435
- `tax`: 1605
- `work_career`: 356
