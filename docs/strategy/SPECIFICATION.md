# 詳細仕様書 (SPECIFICATION) - Ver.2.0

## 1. 機能詳細

### 1.1 認証・認可
- **方式**: Firebase Auth または同等のプロバイダを利用したメールアドレス/パスワード認証。
- **ロール**: `trainer` (管理者) と `trainee` (顧客)。
- **権限**: `trainer` は全ユーザーの予約閲覧・枠設定が可能。`trainee` は自身の予約のみ。

### 1.2 稼働枠管理 (トレーナー用)
- 30分単位で「予約可能」な時間枠をカレンダー上で設定。
- 繰り返し設定（毎週月曜 9:00-18:00 など）への対応検討。

### 1.3 予約フロー (顧客用)
1. コース（時間）の選択。
2. 日付の選択。
3. 指定した時間分の空きがあるスロットを表示。
4. 予約確定（1日前24時以前であることの検証）。

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
- `createdAt`: Timestamp

### 2.3 `users` (ユーザー)
- `id`: String (Auth ID)
- `email`: String (Unique)
- `name`: String
- `phone`: String
- `role`: String (`trainer`, `trainee`)

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
