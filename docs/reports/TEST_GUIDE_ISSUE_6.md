# Issue #6 動作確認ガイド

## 確認の流れ

1. **バックエンドサーバーを起動**
2. **ターミナルでcurlコマンドを実行**
3. **結果を確認**

---

## ステップ1: バックエンドサーバーを起動

新しいターミナルウィンドウを開いて、以下のコマンドを実行します：

```bash
cd /Users/tmk916u/reseve/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

サーバーが起動すると、以下のようなメッセージが表示されます：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
```

**このターミナルは起動したままにしておきます**（Ctrl+Cで停止できます）

---

## ステップ2: 動作確認（別のターミナルで実行）

サーバーが起動したら、**別のターミナルウィンドウ**を開いて、以下の確認項目を実行します。

### 確認項目1: ユーザー情報の更新（正常系）

#### 1-1. まずユーザーを作成

```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"テストユーザー","email":"test@example.com","phone":"090-1234-5678"}' \
  | python3 -m json.tool
```

**実行結果の例：**
```json
{
    "id": "abc123def456",
    "name": "テストユーザー",
    "email": "test@example.com",
    "phone": "090-1234-5678",
    "role": "trainee",
    "createdAt": "2024-12-25T10:00:00.123456",
    "updatedAt": "2024-12-25T10:00:00.123456"
}
```

**`id`の値をコピーしておきます**（次のコマンドで使用します）

#### 1-2. ユーザー情報を更新（名前のみ）

```bash
# USER_IDを実際のIDに置き換えてください
USER_ID="ここに上記で取得したidを貼り付け"

curl -X PUT http://localhost:8000/api/users/$USER_ID \
  -H "Content-Type: application/json" \
  -d '{"name":"更新後の名前"}' \
  | python3 -m json.tool
```

**期待される結果：**
- `name`が「更新後の名前」に変更されている
- `updatedAt`が新しいタイムスタンプになっている
- `createdAt`は変更されていない

---

### 確認項目2: 複数フィールドの同時更新

```bash
# USER_IDは同じものを使用
curl -X PUT http://localhost:8000/api/users/$USER_ID \
  -H "Content-Type: application/json" \
  -d '{"name":"新しい名前","email":"new-email@example.com","phone":"090-9999-9999"}' \
  | python3 -m json.tool
```

**期待される結果：**
- `name`, `email`, `phone`がすべて更新されている
- `updatedAt`が更新されている

---

### 確認項目3: メールアドレスの重複チェック（異常系）

#### 3-1. 別のユーザーを作成

```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"別ユーザー","email":"other@example.com"}' \
  | python3 -m json.tool
```

**`id`をコピーしておきます**

#### 3-2. 最初のユーザーのメールアドレスを、別ユーザーのメールアドレスに変更しようとする

```bash
# USER_IDは最初に作成したユーザーのID
curl -X PUT http://localhost:8000/api/users/$USER_ID \
  -H "Content-Type: application/json" \
  -d '{"email":"other@example.com"}' \
  | python3 -m json.tool
```

**期待される結果：**
```json
{
    "detail": "このメールアドレスは既に使用されています"
}
```
- ステータスコード: `409`

---

### 確認項目4: 存在しないユーザーID（異常系）

```bash
curl -X PUT http://localhost:8000/api/users/non_existent_id_12345 \
  -H "Content-Type: application/json" \
  -d '{"name":"テスト"}' \
  | python3 -m json.tool
```

**期待される結果：**
```json
{
    "detail": "ユーザーが見つかりません"
}
```
- ステータスコード: `404`

---

### 確認項目5: 名前が空文字列（異常系）

```bash
# USER_IDは実際のIDを使用
curl -X PUT http://localhost:8000/api/users/$USER_ID \
  -H "Content-Type: application/json" \
  -d '{"name":""}' \
  | python3 -m json.tool
```

**期待される結果：**
```json
{
    "detail": "名前は空にできません"
}
```
- ステータスコード: `400`

---

### 確認項目6: updatedAtの自動更新確認

```bash
# 更新前のupdatedAtを確認
echo "更新前:"
curl http://localhost:8000/api/users/$USER_ID | python3 -c "import sys, json; print(json.load(sys.stdin)['updatedAt'])"

# 2秒待つ
sleep 2

# 更新実行
curl -X PUT http://localhost:8000/api/users/$USER_ID \
  -H "Content-Type: application/json" \
  -d '{"phone":"090-8888-8888"}' \
  > /dev/null

# 更新後のupdatedAtを確認
echo "更新後:"
curl http://localhost:8000/api/users/$USER_ID | python3 -c "import sys, json; print(json.load(sys.stdin)['updatedAt'])"
```

**期待される結果：**
- 更新後の`updatedAt`が更新前より新しいタイムスタンプになっている

---

## ステップ3: ブラウザでの確認（オプション）

ブラウザで以下のURLを開きます：

```
http://localhost:8000/docs
```

FastAPIの自動生成ドキュメントが表示されます。

1. `PUT /api/users/{user_id}` を探す
2. クリックして展開
3. "Try it out" ボタンをクリック
4. `user_id`に実際のユーザーIDを入力
5. Request bodyにJSONを入力（例: `{"name":"ブラウザから更新"}`）
6. "Execute" ボタンをクリック
7. レスポンスを確認

---

## トラブルシューティング

### サーバーが起動しない場合

- ポート8000が既に使用されている可能性があります
- 別のプロセスを終了するか、ポート番号を変更してください

### curlコマンドがエラーになる場合

- `python3 -m json.tool`がない場合は、最後の `| python3 -m json.tool` を削除して実行してください
- JSONの形式が正しいか確認してください（ダブルクォートを使用）

### Firestoreの認証エラーが出る場合

ローカル環境でFirestoreを使用する場合は、認証が必要です：

```bash
gcloud auth application-default login
```

---

## 確認完了の目安

すべての確認項目を実行し、期待される結果が得られれば、動作確認は完了です。

確認項目をチェックリスト形式で記録すると良いでしょう：

- [ ] 確認項目1: ユーザー情報の更新（正常系）
- [ ] 確認項目2: 複数フィールドの同時更新
- [ ] 確認項目3: メールアドレスの重複チェック（異常系）
- [ ] 確認項目4: 存在しないユーザーID（異常系）
- [ ] 確認項目5: 名前が空文字列（異常系）
- [ ] 確認項目6: updatedAtの自動更新確認
- [ ] 確認項目7: ブラウザでの確認（オプション）

