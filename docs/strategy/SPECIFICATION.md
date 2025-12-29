# 詳細仕様書 (SPECIFICATION) - Ver.2.0

## 1. 機能詳細

### 1.1 認証・認可
- **方式**: Firebase Auth または同等のプロバイダを利用したメールアドレス/パスワード認証。
- **ロール**: `trainer` (管理者) と `trainee` (顧客)。
- **権限**: `trainer` は全ユーザーの予約閲覧・枠設定が可能。`trainee` は自身の予約のみ。
- **マイページ**: ユーザー自身のプロフィール（名前、メール、電話番号）の変更、およびパスワードの変更が可能。

### 1.2 稼働枠管理 (トレーナー用)
- 30分単位で「予約可能」な時間枠をカレンダー上で設定。
- 前週の枠をコピーする機能。

### 1.3 予約フロー (顧客用)
1. トレーナーの選択（任意）。
2. コース（時間）の選択。
3. 日付の選択。
4. 指定した時間分の連続した空きがあるスロットを表示。
5. 予約確定（前日24時以前であることの検証）。

## 2. データモデル (Firestore)

### 2.1 `availabilities` (トレーナー稼働枠)
- `id`: String
- `trainerId`: String
- `startAt`: Timestamp
- `endAt`: Timestamp
- `isBooked`: Boolean (予約が入ったら true)

### 2.2 `reservations` (予約)
- `id`: String
- `traineeId`: String
- `trainerId`: String
- `date`: String (YYYY-MM-DD)
- `startTime`: String (HH:mm)
- `endTime`: String (HH:mm)
- `courseMinutes`: Integer (60, 90, 120...)
- `status`: String (`active`, `cancelled`)
- `startAt`: Timestamp
- `endAt`: Timestamp
- `createdAt`: String (ISO 8601)

### 2.3 `users` (ユーザー)
- `id`: String (Auth ID)
- `email`: String (Unique)
- `name`: String
- `phone`: String
- `role`: String (`trainer`, `trainee`)
- `hashed_password`: String (bcrypt)
- `createdAt`: String (ISO 8601)
- `updatedAt`: String (ISO 8601)

### 2.4 `products` (商品/プランマスタ)
- `id`: String
- `name`: String (例: 600分チケット)
- `price`: Integer
- `type`: String (`ticket`, `monthly`, `one-time`, `fee`, `option`)

## 3. ロジック・計算仕様
### 3.1 予約可否判定
- `startTime` から `courseMinutes` 分の連続した `availabilities` が「未予約」であること。
- 現在時刻が `date` の前日 24:00 以前であること。

### 3.2 キャンセル判定
- 現在時刻が `date` の前日 24:00 以前であること。

## 4. API エンドポイント

### 4.1 認証 (`/api/auth`)
- `POST /signup`: 新規ユーザー登録
- `POST /login`: ログイン (JWT発行)

### 4.2 ユーザー (`/api/users`)
- `GET /me`: 自身のプロフィール取得
- `PATCH /me`: プロフィール更新
- `PUT /me/password`: パスワード更新
- `GET /`: トレーナー一覧取得

### 4.3 稼働枠 (`/api/availabilities`)
- `GET /`: 一覧取得
- `POST /`: 一括登録 (トレーナー専用)
- `DELETE /{id}`: 枠削除 (トレーナー専用)
- `POST /copy-last-week`: 前週コピー

### 4.4 予約 (`/api/reservations`)
- `GET /`: 予約一覧取得
- `POST /`: 予約作成
- `POST /{id}/cancel`: 予約キャンセル
