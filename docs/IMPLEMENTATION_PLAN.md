# mcp-bing-webmaster 実装計画（引き継ぎドキュメント）

> このファイルは別セッション/別フォルダへの引き継ぎ用。単独で読んで実装を再開できるよう自己完結させてある。
> 元の検討は logishift プロジェクトのセッションで実施。ここに全決定事項を集約している。

## 目的

Bing Webmaster Tools を MCP 経由で扱えるようにする、**自作の公開 MCP サーバー**を作る。
既存の個人メンテ OSS（isiahw1/mcp-server-bing-webmaster 等）はサプライチェーン面の懸念があるため、
それらを**参考にしながらゼロから**（クリーン実装で）書き、自分の GitHub で所有・pin して安全性を担保する。

logishift 側には既に GSC(`gsc-logishift`)・GA4(`ga4-logishift`) の MCP があり、その Bing 版という位置づけ。

## 確定した設計判断

| 項目 | 決定 |
|---|---|
| 作り方 | **クリーン書き直し**（既存OSSのコードはコピーしない。ツール名は Bing API メソッド名準拠なので問題なし） |
| ツール範囲 | **読み取り + URL送信のみ**。破壊的操作(remove/add_site/verify/site_move等)は**コードごと不搭載** |
| 配布方式 | **pure Python + uvx**（Node ラッパーは作らない） |
| ライセンス | **MIT**（自分の成果物として。isiahw1 への帰属記載は不要＝クリーン実装のため） |
| クレジット | 入れない（純粋な自作として公開） |
| レポジトリ | `AkiraMatsumoto-github/mcp-bing-webmaster`（ユーザーが空レポジトリで作成済み想定） |
| 実装場所 | `~/development/mcp-bing-webmaster`（clone 先） |

## レポジトリ構成

```
mcp-bing-webmaster/
├── pyproject.toml          # entry point: mcp-bing-webmaster / deps: mcp[cli], httpx（バージョン固定）
├── README.md
├── LICENSE                 # MIT
├── .env.example            # BING_WEBMASTER_API_KEY=
├── .gitignore
├── docs/
│   └── IMPLEMENTATION_PLAN.md   # このファイル
└── src/mcp_bing_webmaster/
    ├── __init__.py
    ├── __main__.py         # uvx エントリポイント（server.run() を呼ぶ）
    ├── server.py           # FastMCP 定義・ツール登録
    └── client.py           # Bing API HTTP クライアント（httpx, 全リクエスト timeout 付き）
```

## Bing Webmaster API 仕様（実装の要）

- ベースURL: `https://ssl.bing.com/webmaster/api.svc/json/{Method}?apikey={API_KEY}`
- 認証: API キーを **クエリパラメータ `apikey`** で渡す（環境変数 `BING_WEBMASTER_API_KEY` から読む。コードに埋め込まない）
- GET/POST は メソッドにより異なる（送信系は POST + JSON ボディ）
- 公式リファレンス: https://learn.microsoft.com/en-us/bingwebmaster/ （実装時にメソッド名/引数を必ず照合すること）

### 搭載するツール（読み取り）
- `get_sites`  … GetUserSites
- `get_query_stats`  … GetQueryStats（siteUrl）
- `get_page_stats`  … GetPageStats
- `get_page_query_stats`  … GetPageQueryStats
- `get_rank_and_traffic_stats`  … GetRankAndTrafficStats
- `get_url_traffic_info`  … GetUrlTrafficInfo
- `get_crawl_stats`  … GetCrawlStats
- `get_crawl_issues`  … GetCrawlIssues
- `get_url_info`  … GetUrlInfo
- `get_keyword_stats`  … GetKeywordStats
- `get_related_keywords`  … GetRelatedKeywords
- `get_link_counts`  … GetLinkCounts
- `get_url_submission_quota`  … GetUrlSubmissionQuota
- `get_content_submission_quota`  … GetContentSubmissionQuota

### 搭載するツール（URL送信・非破壊）
- `submit_url`  … SubmitUrl（siteUrl, url）
- `submit_url_batch`  … SubmitUrlBatch（siteUrl, urlList[]）
- `submit_sitemap`  … 該当メソッド確認のうえ実装（feed/sitemap 送信）

### 不搭載（意図的に実装しない）
`remove_site` / `add_site` / `verify_site` / `add_site_roles` / `submit_site_move` /
`update_crawl_settings` / `remove_sitemap` / `add/remove_blocked_url` /
`add/remove_deep_link_block` / `add/remove_query_parameter` /
`add/remove_country_region_settings` / `add/remove_page_preview_block` 等、破壊的・設定変更系すべて。

## セキュリティ是正（既存OSSからの改善点）

1. **env 全継承を廃止** … Node ラッパー(`run.js`)の `env:{...process.env}` が問題だった。pure Python で `BING_WEBMASTER_API_KEY` のみ参照。
2. **破壊的ツールを実装しない** … 誤爆リスクを設計段階で排除。
3. **通信先を限定** … `ssl.bing.com` のみへ HTTP。テレメトリ等の第三者送信なし。
4. **全リクエストに timeout** … httpx のタイムアウトを明示設定。
5. **バージョン pin** … 依存を pyproject で固定。呼び出し側も `@latest` でなくタグ pin。
6. **APIキーをコードに埋め込まない** … .env / 環境変数のみ。README で明記。

## logishift 側の呼び出し設定

`~/development/logishift/.mcp.json` の `mcpServers` に追記（**pin したタグを指定**）：

```json
"bing-logishift": {
  "command": "uvx",
  "args": [
    "--from",
    "git+https://github.com/AkiraMatsumoto-github/mcp-bing-webmaster@v0.1.0",
    "mcp-bing-webmaster"
  ],
  "env": {
    "BING_WEBMASTER_API_KEY": "<発行後に設定>"
  }
}
```

## 残タスク / 手順

1. [x] clone 先 `~/development/mcp-bing-webmaster` にレポジトリ雛形＋全コード作成
2. [x] pyproject / README / LICENSE(MIT) / .env.example / .gitignore
3. [x] client.py（Bing API クライアント）・server.py（FastMCP・ツール登録）・__main__.py
4. [x] ローカル起動確認（`uv sync` 成功／16ツール登録／キー未設定時は明確なエラー／stdio起動OK）
5. [ ] commit → push → **タグ付け（v0.1.0）**  ← push はユーザー確認待ち
6. [ ] logishift の `.mcp.json` に `bing-logishift` 追記
7. [ ] **【APIキー発行後】** ライブ疎通確認（`get_sites` で実データ取得）

### 実装メモ（v0.1.0 時点）
- 登録ツール16個（読み取り14 + 送信2）。破壊系は不搭載。
- `get_keyword_stats` / `get_related_keywords` は API シグネチャが未検証（provisional）。キー入手後に実データで確認。
- `submit_sitemap` は公式 API に確実なメソッドが無いため**不搭載**。
- レスポンスは `{"d": ...}` を自動アンラップ。エラーは例外で落とさず `{"error":..., "error_code":...}` を返す。

## 保留事項

- **Bing Webmaster API キーが未発行**。発行先: https://www.bing.com/webmasters → 設定 → API アクセス。
  発行までは 1〜6 まで進め、7（ライブ疎通確認）のみ保留。