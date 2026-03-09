# TikTok Live Center → Google Sheets 自動記録ツール

TikTok ライブセンターの分析データを毎日自動でGoogleスプレッドシートに記録するPythonスクリプトです。

## 記録される項目

| カテゴリ | 項目 |
|---------|------|
| 基本情報 | 日付, LIVE名, LIVE時間, 新規フォロワー |
| 視聴 | 視聴数, ユニーク視聴者数, アクティブな視聴者, 最高同時視聴者数, 平均視聴時間 |
| エンゲージメント | コメント, いいね, シェア, ギフト贈呈者 |
| トラフィックのソース | LIVEのおすすめ(%), あなたの投稿(%), フォロー中フィード(%), シェア_トラフィック(%), その他(%) |
| フォロワー | 平均視聴時間, ユニーク視聴者数, コメント投稿者, ギフト贈呈者 |
| 報酬 | 推定額(USD), ダイヤモンド, このLIVEの% |

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Google Sheets APIの設定

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. **Google Sheets API** と **Google Drive API** を有効化
3. 「APIとサービス」→「認証情報」→「認証情報を作成」→ **OAuthクライアントID** を選択
4. アプリの種類: **デスクトップアプリ** を選択して作成
5. ダウンロードしたJSONを `credentials.json` としてこのディレクトリに配置
6. 初回実行時にブラウザが開くので、Googleアカウントで認証してください（以降は `token.pickle` に保存され自動化されます）

### 3. 環境設定

```bash
cp .env.example .env
```

`.env` を編集して以下を設定：

```
SPREADSHEET_ID=スプレッドシートのID（URLの /d/ と /edit の間の文字列）
SHEET_NAME=TikTok LIVE
GOOGLE_CREDENTIALS_FILE=credentials.json
SCHEDULE_TIME=09:00
```

### 4. TikTokログイン（初回のみ）

```bash
python auth.py
```

ブラウザが開くので、TikTokにログインしてEnterを押してください。
Cookieが `cookies.json` に保存されます。

## 使い方

### 手動実行（昨日のデータを取得）

```bash
python main.py
```

### 特定の日付を指定

```bash
python main.py --date 2026-03-09
```

### 毎日自動実行（スケジューラー）

```bash
# Python内蔵スケジューラーで常時起動
python main.py --scheduler
```

または、cronで自動実行するよう設定：

```bash
bash setup_cron.sh
```

デフォルトは毎日09:00 JSTに前日データを取得します（`.env` の `SCHEDULE_TIME` で変更可）。

## ファイル構成

```
.
├── main.py              # エントリポイント
├── scraper.py           # Playwright スクレイパー
├── sheets.py            # Google Sheets 書き込み
├── auth.py              # TikTok 認証（Cookie保存）
├── config.py            # 設定読み込み
├── requirements.txt     # 依存パッケージ
├── .env.example         # 環境変数テンプレート
├── setup_cron.sh        # cron設定ヘルパー
├── cookies.json         # TikTok Cookie（自動生成・gitignore対象）
└── credentials.json     # Google認証情報（gitignore対象）
```

## 注意事項

- `cookies.json` と `credentials.json` はGitにコミットしないでください（`.gitignore` 設定済み）
- TikTokのCookieは定期的に期限切れになります。その場合は `python auth.py` を再実行してください
- TikTokのページ構造が変わった場合は `scraper.py` のセレクター調整が必要になることがあります
