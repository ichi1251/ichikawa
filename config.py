import os
from dotenv import load_dotenv

load_dotenv()

# Google Sheets
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")
SHEET_NAME = os.getenv("SHEET_NAME", "TikTok LIVE")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

# TikTok
TIKTOK_LIVE_CENTER_URL = "https://www.tiktok.com/tiktok-live-studio/web/"
COOKIES_FILE = "cookies.json"

# Scheduler: time to run daily (24h format)
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "09:00")

# Spreadsheet column headers
HEADERS = [
    "日付",
    "LIVE名",
    "LIVE時間",
    # 視聴
    "視聴数",
    "ユニーク視聴者数",
    "アクティブな視聴者",
    "最高同時視聴者数",
    "平均視聴時間",
    # エンゲージメント
    "コメント",
    "いいね",
    "シェア",
    "ギフト贈呈者",
    # トラフィックのソース
    "LIVEのおすすめ(%)",
    "あなたの投稿(%)",
    "フォロー中フィード(%)",
    "シェア_トラフィック(%)",
    "その他(%)",
    # フォロワー
    "フォロワー_平均視聴時間",
    "フォロワー_ユニーク視聴者数",
    "フォロワー_コメント投稿者",
    "フォロワー_ギフト贈呈者",
    # 報酬
    "推定額(USD)",
    "ダイヤモンド",
    "このLIVEの%",
    # 集計列
    "新規フォロワー",
]
