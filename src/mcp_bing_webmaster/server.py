"""FastMCP server exposing a curated, non-destructive subset of the
Bing Webmaster Tools API.

Only read ("get_*") and URL-submission ("submit_*") tools are registered.
Destructive operations (remove_site, verify_site, submit_site_move,
update_crawl_settings, *_blocked_url, etc.) are intentionally not implemented.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import BingWebmasterClient, BingWebmasterError

mcp = FastMCP("bing-webmaster")

_client: BingWebmasterClient | None = None


def _get_client() -> BingWebmasterClient:
    """Lazily construct the client so the server can start without a key
    and surface a clear error only when a tool is actually invoked."""
    global _client
    if _client is None:
        _client = BingWebmasterClient()
    return _client


def _call_get(method: str, params: dict[str, Any] | None = None) -> Any:
    try:
        return _get_client().get(method, params)
    except BingWebmasterError as exc:
        return {"error": str(exc), "error_code": exc.error_code}


def _call_post(method: str, body: dict[str, Any] | None = None) -> Any:
    try:
        return _get_client().post(method, body)
    except BingWebmasterError as exc:
        return {"error": str(exc), "error_code": exc.error_code}


# --- Read: sites & traffic ------------------------------------------------

@mcp.tool()
def get_sites() -> Any:
    """List all sites verified for the authenticated Bing Webmaster account."""
    return _call_get("GetUserSites")


@mcp.tool()
def get_query_stats(site_url: str) -> Any:
    """Get search query statistics (impressions, clicks, position) for a site.

    site_url: a verified site, e.g. "https://example.com".
    """
    return _call_get("GetQueryStats", {"siteUrl": site_url})


@mcp.tool()
def get_page_stats(site_url: str) -> Any:
    """Get per-page traffic statistics for a verified site."""
    return _call_get("GetPageStats", {"siteUrl": site_url})


@mcp.tool()
def get_page_query_stats(site_url: str, page: str) -> Any:
    """Get the search queries that drove traffic to a specific page.

    page: the full page URL to inspect.
    """
    return _call_get("GetPageQueryStats", {"siteUrl": site_url, "page": page})


@mcp.tool()
def get_rank_and_traffic_stats(site_url: str) -> Any:
    """Get daily impressions/clicks rank & traffic time series for a site."""
    return _call_get("GetRankAndTrafficStats", {"siteUrl": site_url})


@mcp.tool()
def get_url_traffic_info(site_url: str, url: str) -> Any:
    """Get index traffic details (clicks, impressions) for a single page.

    A "domain:" prefix on url returns domain-level info, e.g. "domain:example.com".
    """
    return _call_get("GetUrlTrafficInfo", {"siteUrl": site_url, "url": url})


# --- Read: crawl & indexing ----------------------------------------------

@mcp.tool()
def get_crawl_stats(site_url: str) -> Any:
    """Get crawl statistics (crawled pages, errors, blocked) for a site."""
    return _call_get("GetCrawlStats", {"siteUrl": site_url})


@mcp.tool()
def get_crawl_issues(site_url: str) -> Any:
    """Get crawl issues Bing has detected for a site."""
    return _call_get("GetCrawlIssues", {"siteUrl": site_url})


@mcp.tool()
def get_url_info(site_url: str, url: str) -> Any:
    """Get Bing's index information for a single URL."""
    return _call_get("GetUrlInfo", {"siteUrl": site_url, "url": url})


@mcp.tool()
def get_link_counts(site_url: str, page: int = 0) -> Any:
    """Get inbound link counts for a site.

    page: zero-based pagination index for large result sets.
    """
    return _call_get("GetLinkCounts", {"siteUrl": site_url, "page": page})


# --- Read: quota ----------------------------------------------------------

@mcp.tool()
def get_url_submission_quota(site_url: str) -> Any:
    """Get remaining daily/monthly URL submission quota for a site."""
    return _call_get("GetUrlSubmissionQuota", {"siteUrl": site_url})


@mcp.tool()
def get_content_submission_quota(site_url: str) -> Any:
    """Get remaining content submission quota for a site."""
    return _call_get("GetContentSubmissionQuota", {"siteUrl": site_url})


# --- Read: keywords (provisional signatures; validate with a live key) ----

@mcp.tool()
def get_keyword_stats(query: str, country: str, language: str) -> Any:
    """Get impression statistics for a keyword.

    country: two-letter market/country code (e.g. "jp").
    language: language code (e.g. "ja-JP").
    Note: parameter shape follows the documented API signature and should be
    validated against a live account.
    """
    return _call_get(
        "GetKeywordStats",
        {"q": query, "country": country, "language": language},
    )


@mcp.tool()
def get_related_keywords(query: str, country: str, language: str) -> Any:
    """Get keywords related to the given query.

    Note: parameter shape follows the documented API signature and should be
    validated against a live account.
    """
    return _call_get(
        "GetRelatedKeywords",
        {"q": query, "country": country, "language": language},
    )


# --- Submit: URLs (non-destructive; consumes submission quota) ------------

@mcp.tool()
def submit_url(site_url: str, url: str) -> Any:
    """Submit a single URL to Bing for (re)crawling. Consumes URL quota."""
    return _call_post("SubmitUrl", {"siteUrl": site_url, "url": url})


@mcp.tool()
def submit_url_batch(site_url: str, url_list: list[str]) -> Any:
    """Submit a batch of URLs to Bing for (re)crawling. Consumes URL quota.

    url_list: list of absolute URLs belonging to site_url.
    """
    return _call_post("SubmitUrlBatch", {"siteUrl": site_url, "urlList": url_list})
