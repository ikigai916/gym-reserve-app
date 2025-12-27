# アーキテクチャ仕様書 (ARCHITECTURE) - Ver.2.0

## 1. コンセプト
Google Cloud のマネージドサービスをフル活用した、スケーラブルかつセキュアな構成。

## 2. 技術スタック
- **Backend**: FastAPI (Python 3.11)
  - 30分単位の時間枠計算およびバリデーションを担う。
- **Frontend**: HTML / Tailwind CSS / Alpine.js
  - FastAPI から静的ファイルとして配信。
- **Auth**: Firebase Auth (検討中) または FastAPI 上での JWT 認証。
  - セキュリティを重視し、パスワード認証を導入。
- **Database**: Google Cloud Firestore
  - スキーマレスの利点を活かし、`availabilities` と `reservations` を紐付け。
- **Hosting**: Google Cloud Run
  - Dockerコンテナとして実行。

## 3. データの流れ
### 3.1 予約受付の整合性
1. クライアントが希望のコースと時間を送信。
2. FastAPI が Firestore から `availabilities` を取得。
3. 連続する空きスロットがあるか、期限内かをサーバーサイドで厳密にチェック。
4. `availabilities` を `isBooked: true` に更新し、同時に `reservations` を作成（トランザクション処理）。

## 4. 拡張性への考慮
- **マルチテナント**: 将来的な他店舗展開を考慮し、店舗ID（StudioID）の付与を想定。
- **決済連携**: Webhook を受け取れる構造にし、Stripe との統合を容易にする。
- **カルテ記録**: 大カテゴリ・中カテゴリの動的追加に対応できる柔軟なデータ構造を保持。
