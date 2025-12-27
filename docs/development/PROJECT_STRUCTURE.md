# プロジェクト構造（新しい技術スタック）

## ディレクトリ構造

```
reseve/
├── backend/                    # FastAPI バックエンド
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPIアプリケーションのエントリーポイント
│   │   ├── models.py          # データモデル（User, Reservation）
│   │   ├── schemas.py         # Pydanticスキーマ
│   │   ├── routers/           # APIルーター
│   │   │   ├── __init__.py
│   │   │   ├── reservations.py
│   │   │   └── users.py
│   │   └── storage.py         # データ永続化（JSONファイル操作）
│   ├── data/                  # データファイル保存先
│   │   ├── reservations.json
│   │   └── users.json
│   ├── requirements.txt       # Python依存パッケージ
│   ├── .env.example           # 環境変数の例
│   └── README.md
│
├── frontend/                   # HTML + Alpine.js + Tailwind CSS
│   ├── index.html             # メインHTMLファイル
│   ├── css/
│   │   └── style.css          # Tailwind CSS（ビルド後）
│   ├── js/
│   │   ├── app.js             # Alpine.jsアプリケーションロジック
│   │   └── utils.js           # ユーティリティ関数（ユーザーID管理など）
│   ├── package.json           # Bun用（Tailwind CSSビルド用）
│   └── tailwind.config.js     # Tailwind CSS設定
│
├── .gitignore
├── README.md
└── specification.md
```

## 技術スタック詳細

### Backend
- **Python 3.11+**
- **FastAPI**: モダンなPython Webフレームワーク
- **Pydantic**: データバリデーション
- **uvicorn**: ASGIサーバー

### Frontend
- **HTML5**: シンプルなHTML
- **Alpine.js**: 軽量なリアクティブフレームワーク
- **Tailwind CSS**: ユーティリティファーストのCSSフレームワーク

### Package Manager
- **Bun**: JavaScript/TypeScriptのパッケージマネージャー（Tailwind CSSビルド用）

