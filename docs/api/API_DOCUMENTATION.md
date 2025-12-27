# API ドキュメント

## ベースURL

- 開発環境: `http://localhost:8000`
- 本番環境: `https://gym-reserve-app-1094873497912.asia-northeast1.run.app`

## 認証

現在は簡易的な認証方式を使用：
- ユーザーIDをローカルストレージで管理
- 各APIリクエストでユーザーIDを送信

## エンドポイント一覧

### ヘルスチェック

#### GET /health

ヘルスチェックエンドポイント

**レスポンス:**
```json
{
  "status": "ok",
  "service": "gym-reservation-api"
}
```

---

### ユーザー関連

#### POST /api/users

ユーザーを作成します。

**リクエストボディ:**
```json
{
  "name": "山田太郎",
  "email": "yamada@example.com",
  "phone": "090-1234-5678",
  "role": "trainee"
}
```

**パラメータ:**
- `name` (string, 必須): ユーザー名
- `email` (string, オプション): メールアドレス
- `phone` (string, オプション): 電話番号
- `role` (string, オプション): ロール（"trainer" または "trainee"、デフォルトは "trainee"）

**レスポンス:**
```json
{
  "id": "user_id_123",
  "name": "山田太郎",
  "email": "yamada@example.com",
  "phone": "090-1234-5678",
  "role": "trainee",
  "createdAt": "2024-12-25T10:00:00",
  "updatedAt": "2024-12-25T10:00:00"
}
```

**ステータスコード:**
- `200`: 成功
- `400`: バリデーションエラー（名前が空など）
- `500`: サーバーエラー

---

#### GET /api/users/{user_id}

ユーザー情報を取得します。

**パスパラメータ:**
- `user_id` (string, 必須): ユーザーID

**レスポンス:**
```json
{
  "id": "user_id_123",
  "name": "山田太郎",
  "email": "yamada@example.com",
  "phone": "090-1234-5678",
  "role": "trainee",
  "createdAt": "2024-12-25T10:00:00",
  "updatedAt": "2024-12-25T10:00:00"
}
```

**ステータスコード:**
- `200`: 成功
- `404`: ユーザーが見つからない
- `500`: サーバーエラー

---

#### PUT /api/users/{user_id}

ユーザー情報を更新します。

**パスパラメータ:**
- `user_id` (string, 必須): ユーザーID

**リクエストボディ:**
```json
{
  "name": "山田花子",
  "email": "yamada-hanako@example.com",
  "phone": "090-9876-5432"
}
```

**パラメータ:**
- `name` (string, オプション): ユーザー名（空文字列は不可）
- `email` (string, オプション): メールアドレス（空文字列可）
- `phone` (string, オプション): 電話番号（空文字列可）

**注意事項:**
- すべてのフィールドはオプションです（指定したフィールドのみ更新されます）
- `role`フィールドは更新できません（セキュリティ上の理由）
- メールアドレスは他のユーザーと重複できません
- `updatedAt`フィールドは自動的に更新されます
- `createdAt`フィールドは変更されません

**レスポンス:**
```json
{
  "id": "user_id_123",
  "name": "山田花子",
  "email": "yamada-hanako@example.com",
  "phone": "090-9876-5432",
  "role": "trainee",
  "createdAt": "2024-12-25T10:00:00",
  "updatedAt": "2024-12-25T11:30:00"
}
```

**ステータスコード:**
- `200`: 成功
- `400`: バリデーションエラー（名前が空など）
- `404`: ユーザーが見つからない
- `409`: メールアドレスが既に使用されている
- `500`: サーバーエラー

---

### 予約関連

#### POST /api/reservations

予約を作成します（新形式）。

**リクエストボディ:**
```json
{
  "userId": "user_id_123",
  "date": "2024-12-25",
  "timeSlot": "09:00-10:00",
  "trainerId": null,
  "menuId": null,
  "userPlanId": null
}
```

**パラメータ:**
- `userId` (string, 必須): ユーザーID
- `date` (string, 必須): 予約日（YYYY-MM-DD形式）
- `timeSlot` (string, 必須): 時間枠（例: "09:00-10:00"）
- `trainerId` (string, オプション): トレーナーID（将来必須化予定）
- `menuId` (string, オプション): メニューID（将来必須化予定）
- `userPlanId` (string, オプション): ユーザープランID（将来必須化予定）

**レスポンス:**
```json
{
  "id": "reservation_id_456",
  "userId": "user_id_123",
  "user_name": "山田太郎",
  "date": "2024-12-25",
  "timeSlot": "09:00-10:00",
  "status": "active",
  "trainerId": null,
  "menuId": null,
  "userPlanId": null,
  "createdAt": "2024-12-25T10:00:00",
  "updatedAt": "2024-12-25T10:00:00"
}
```

**ステータスコード:**
- `200`: 成功
- `400`: バリデーションエラー（必須パラメータが不足など）
- `404`: ユーザーが見つからない
- `500`: サーバーエラー

---

#### GET /api/reservations

予約一覧を取得します（新形式）。

**クエリパラメータ（将来実装予定）:**
- `userId` (string, オプション): ユーザーIDでフィルタリング
- `status` (string, オプション): ステータスでフィルタリング（"active" または "cancelled"）

**レスポンス:**
```json
[
  {
    "id": "reservation_id_456",
    "userId": "user_id_123",
    "user_name": "山田太郎",
    "date": "2024-12-25",
    "timeSlot": "09:00-10:00",
    "status": "active",
    "trainerId": null,
    "menuId": null,
    "userPlanId": null,
    "createdAt": "2024-12-25T10:00:00",
    "updatedAt": "2024-12-25T10:00:00"
  }
]
```

**ステータスコード:**
- `200`: 成功
- `500`: サーバーエラー

---

#### POST /reservations

予約を作成します（旧形式、後方互換性のため残す）。

**リクエストボディ:**
```json
{
  "user_name": "山田太郎",
  "date": "2024-12-25"
}
```

**レスポンス:**
```json
{
  "message": "予約が完了しました！",
  "id": "reservation_id_456"
}
```

---

#### GET /reservations

予約一覧を取得します（旧形式、後方互換性のため残す）。

**レスポンス:**
```json
[
  {
    "id": "reservation_id_456",
    "user_name": "山田太郎",
    "date": "2024-12-25",
    "created_at": "2024-12-25T10:00:00"
  }
]
```

---

## エラーレスポンス

### エラーレスポンス形式

```json
{
  "detail": "エラーメッセージ"
}
```

### ステータスコード

- `400`: バリデーションエラー
- `404`: リソースが見つからない
- `500`: サーバーエラー

### エラーメッセージ例

- `"名前は必須です"`: ユーザー作成時に名前が空
- `"userId、date、timeSlotは必須です"`: 予約作成時に必須パラメータが不足
- `"ユーザーが見つかりません"`: 指定されたユーザーIDが存在しない
- `"Firestoreへのアクセス権限がありません"`: Firestoreの権限エラー

---

## データモデル

### User

```typescript
{
  id: string;
  name: string;
  email: string;
  phone: string;
  role: "trainer" | "trainee";
  createdAt: string;
  updatedAt: string;
}
```

### Reservation

```typescript
{
  id: string;
  userId: string;
  user_name: string;
  date: string; // YYYY-MM-DD
  timeSlot: string; // "09:00-10:00"
  status: "active" | "cancelled";
  trainerId?: string;
  menuId?: string;
  userPlanId?: string;
  createdAt: string;
  updatedAt: string;
}
```

---

## 注意事項

1. **新形式APIの使用を推奨**
   - `POST /api/reservations` と `GET /api/reservations` の使用を推奨
   - 旧形式API（`/reservations`）は後方互換性のため残していますが、将来的に削除予定

2. **既存データとの互換性**
   - 既存の予約データ（旧形式）も新形式APIで取得可能
   - 新フィールド（trainerId, menuId, userPlanId）がない場合は `null` が返されます

3. **ロール管理**
   - ユーザー作成時にロールを指定可能
   - デフォルトは "trainee"
   - 既存ユーザー（roleフィールドなし）は "trainee" として扱われます

