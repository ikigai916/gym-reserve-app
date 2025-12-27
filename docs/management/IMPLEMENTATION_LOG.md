# 実装ログ (IMPLEMENTATION LOG)

## 2025-12-27: Cloud Run 起動エラーの修正

### 変更の背景
- 本番環境（Cloud Run）へのデプロイ時に `container failed to start and listen on the port 8080` エラーが発生。
- 原因調査の結果、`app/main.py` 内で既に削除済みのレガシー関数（`get_reservations_legacy`, `create_reservation_legacy`）をインポートしようとして `ImportError` が発生し、アプリケーションの起動が中断されていたことが判明。

### 主要な変更点
1. **`app/main.py` のクリーンアップ**:
   - 存在しないエンドポイントへのインポートとルーティング処理を削除。
   - 静的ファイルの配信設定（`/assets`, `/`, `/index.html`, `/login.html`）は維持。

### 技術的決定
- インフラ（Cloud Run）の設定自体には問題がなかったため、アプリケーションコードの整合性を修正することで対応。

---

## 2025-12-27: トレーニー用UI強化と稼働枠管理の最適化

... (以降、既存のログ)
