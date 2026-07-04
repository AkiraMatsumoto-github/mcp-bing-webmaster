# mcp-bing-webmaster

A small, security-conscious [MCP](https://modelcontextprotocol.io) server for
**Bing Webmaster Tools**. It exposes **read-only** analytics/indexing tools plus
**non-destructive URL submission** — and nothing else.

Written from scratch in pure Python on top of the official
[`mcp`](https://pypi.org/project/mcp/) SDK (FastMCP). No Node wrapper, no
telemetry, and it only ever talks to `ssl.bing.com`.

## Why this exists

Existing community Bing MCP servers ship the full API surface, including
destructive operations (removing sites/sitemaps, site moves, crawl-setting
changes) and, in some cases, a Node launcher that inherits the entire process
environment. This server deliberately:

- **omits every destructive/mutating endpoint** — an agent cannot remove a
  site, sitemap, block, or trigger a site move because those tools do not exist;
- reads the API key **only** from `BING_WEBMASTER_API_KEY` (never a CLI arg,
  never hard-coded);
- talks to a single host (`ssl.bing.com`) with an explicit request timeout;
- pins its dependencies and is meant to be pinned by tag when consumed.

## Requirements

- Python 3.10+
- A Bing Webmaster Tools API key — generate one at
  <https://www.bing.com/webmasters> → **Settings → API access**.

## Usage

Expose your key and run via `uvx` (no install needed):

```bash
export BING_WEBMASTER_API_KEY="your-key"
uvx --from git+https://github.com/AkiraMatsumoto-github/mcp-bing-webmaster@v0.1.0 mcp-bing-webmaster
```

### MCP client config

Pin to a tag so you always run reviewed code:

```json
{
  "mcpServers": {
    "bing-webmaster": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/AkiraMatsumoto-github/mcp-bing-webmaster@v0.1.0",
        "mcp-bing-webmaster"
      ],
      "env": {
        "BING_WEBMASTER_API_KEY": "your-key"
      }
    }
  }
}
```

## Tools

### Read (safe)

| Tool | Bing method | Purpose |
|---|---|---|
| `get_sites` | GetUserSites | List verified sites |
| `get_query_stats` | GetQueryStats | Query impressions/clicks/position |
| `get_page_stats` | GetPageStats | Per-page traffic |
| `get_page_query_stats` | GetPageQueryStats | Queries driving one page |
| `get_rank_and_traffic_stats` | GetRankAndTrafficStats | Daily traffic time series |
| `get_url_traffic_info` | GetUrlTrafficInfo | Traffic for a single URL |
| `get_crawl_stats` | GetCrawlStats | Crawl statistics |
| `get_crawl_issues` | GetCrawlIssues | Detected crawl issues |
| `get_url_info` | GetUrlInfo | Index info for a URL |
| `get_link_counts` | GetLinkCounts | Inbound link counts |
| `get_url_submission_quota` | GetUrlSubmissionQuota | Remaining URL quota |
| `get_content_submission_quota` | GetContentSubmissionQuota | Remaining content quota |
| `get_keyword_stats` | GetKeywordStats | Keyword impressions¹ |
| `get_related_keywords` | GetRelatedKeywords | Related keywords¹ |

¹ Keyword tool parameters follow the documented API signature and should be
validated against a live account.

### Submit (non-destructive, consumes quota)

| Tool | Bing method | Purpose |
|---|---|---|
| `submit_url` | SubmitUrl | Submit one URL for (re)crawl |
| `submit_url_batch` | SubmitUrlBatch | Submit a batch of URLs |

### Intentionally **not** implemented

`remove_site`, `add_site`, `verify_site`, `add_site_roles`, `submit_site_move`,
`update_crawl_settings`, `remove_sitemap`, `add/remove_blocked_url`,
`add/remove_deep_link_block`, `add/remove_query_parameter`,
`add/remove_country_region_settings`, `add/remove_page_preview_block`.

## Development

```bash
uv sync
uv run python -c "import mcp_bing_webmaster.server as s; print([t.name for t in __import__('asyncio').run(s.mcp.list_tools())])"
```

## License

MIT — see [LICENSE](LICENSE).
