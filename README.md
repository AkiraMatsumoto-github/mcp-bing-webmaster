# mcp-bing-webmaster

**Bing Webmaster Tools** 用の、セキュリティを重視した小さな [MCP](https://modelcontextprotocol.io) サーバーです。**読み取り系**の分析・インデックス情報ツールと、**非破壊の URL 送信**ツールだけを提供します。それ以外の操作は搭載しません。

公式 [`mcp`](https://pypi.org/project/mcp/) SDK（FastMCP）の上に、純 Python でゼロから実装しています。Node ラッパーなし、テレメトリなし、通信先は `ssl.bing.com` のみです。

## なぜ作ったか

既存のコミュニティ製 Bing MCP サーバーは API の全機能を載せており、破壊的操作（サイト・サイトマップの削除、サイト移行、クロール設定変更など）を含みます。また一部はプロセスの全環境変数を継承する Node ランチャーを使っています。本サーバーは意図的に次の設計にしています。

- **破壊的・変更系エンドポイントをすべて省略** — サイト・サイトマップ・ブロックの削除やサイト移行のツールは*存在しない*ため、エージェントが誤って実行できません。
- API キーは **`BING_WEBMASTER_API_KEY` 環境変数からのみ**取得（CLI 引数やハードコードは不可）。
- 通信先は単一ホスト（`ssl.bing.com`）のみ。全リクエストに明示的なタイムアウトを設定。
- 依存関係を固定し、利用側もタグ pin で参照する前提。

## 必要要件

- Python 3.10 以上
- Bing Webmaster Tools の API キー — <https://www.bing.com/webmasters> → **設定 → API アクセス** で発行

## 使い方

キーを環境変数に設定し、`uvx` で実行します（インストール不要）。

```bash
export BING_WEBMASTER_API_KEY="あなたのキー"
uvx --from git+https://github.com/AkiraMatsumoto-github/mcp-bing-webmaster@v0.1.0 mcp-bing-webmaster
```

### MCP クライアント設定

必ずタグを pin して、レビュー済みのコードだけを実行してください。

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
        "BING_WEBMASTER_API_KEY": "あなたのキー"
      }
    }
  }
}
```

## ツール一覧

### 読み取り（安全）

| ツール | Bing メソッド | 用途 |
|---|---|---|
| `get_sites` | GetUserSites | 検証済みサイトの一覧 |
| `get_query_stats` | GetQueryStats | クエリ別の表示回数・クリック・順位 |
| `get_page_stats` | GetPageStats | ページ別トラフィック |
| `get_page_query_stats` | GetPageQueryStats | 特定ページへ流入したクエリ |
| `get_rank_and_traffic_stats` | GetRankAndTrafficStats | 日次トラフィックの時系列 |
| `get_url_traffic_info` | GetUrlTrafficInfo | 単一 URL のトラフィック情報 |
| `get_crawl_stats` | GetCrawlStats | クロール統計 |
| `get_crawl_issues` | GetCrawlIssues | 検出されたクロール問題 |
| `get_url_info` | GetUrlInfo | URL のインデックス情報 |
| `get_link_counts` | GetLinkCounts | 被リンク数 |
| `get_url_submission_quota` | GetUrlSubmissionQuota | URL 送信の残クォータ |
| `get_content_submission_quota` | GetContentSubmissionQuota | コンテンツ送信の残クォータ |
| `get_keyword_stats` | GetKeywordStats | キーワードの表示回数¹ |
| `get_related_keywords` | GetRelatedKeywords | 関連キーワード¹ |

¹ キーワード系ツールのパラメータは公式 API のシグネチャに準拠していますが、未検証です。実アカウントで検証のうえ利用してください。

### 送信（非破壊・クォータを消費）

| ツール | Bing メソッド | 用途 |
|---|---|---|
| `submit_url` | SubmitUrl | 単一 URL を（再）クロール向けに送信 |
| `submit_url_batch` | SubmitUrlBatch | 複数 URL を一括送信 |

### 意図的に**搭載していない**操作

`remove_site`、`add_site`、`verify_site`、`add_site_roles`、`submit_site_move`、`update_crawl_settings`、`remove_sitemap`、`add/remove_blocked_url`、`add/remove_deep_link_block`、`add/remove_query_parameter`、`add/remove_country_region_settings`、`add/remove_page_preview_block`。

## 開発

```bash
uv sync
uv run python -c "import mcp_bing_webmaster.server as s; print([t.name for t in __import__('asyncio').run(s.mcp.list_tools())])"
```

## ライセンス

MIT — [LICENSE](LICENSE) を参照してください。
