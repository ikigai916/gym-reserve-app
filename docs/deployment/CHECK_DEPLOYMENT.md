# デプロイの確認方法

## 1. GitHub Actionsのログを確認

### ログの見方

1. GitHubリポジトリのページにアクセス
2. 上部の「**Actions**」タブをクリック
3. 左側のワークフロー一覧から「**Deploy to Cloud Run**」をクリック
4. 最新の実行（一番上）をクリック
5. 「**Deploy to Cloud Run**」というステップを展開

### 確認すべきポイント

- **エラーメッセージがないか**
  - エラーが表示されていれば、その内容を確認
- **デプロイが完了しているか**
  - 「Deploy to Cloud Run」ステップが緑色のチェックマークになっているか
- **gcloudコマンドの出力**
  - `gcloud run deploy`コマンドの出力を確認
  - エラーがなければ、通常は最後にサービスのURLが表示されます

### メッセージについて

「Service deployed successfully」や「Allowing unauthenticated invocations」というメッセージが表示されなくても、デプロイが成功している可能性があります。

gcloudコマンドの出力形式はバージョンによって異なるため、以下のように確認してください：

1. **デプロイステップが成功しているか**（緑色のチェックマーク）
2. **エラーメッセージがないか**
3. **実際にURLにアクセスして動作確認**

---

## 2. GCPコンソールで確認

### Cloud Runサービスが更新されているか確認

1. [GCPコンソール](https://console.cloud.google.com/)にアクセス
2. 「**Cloud Run**」をクリック
3. 「**gym-reserve-app**」サービスをクリック
4. 「**リビジョン**」タブで、最新のリビジョンの作成日時を確認
5. 最新のリビジョンが、先ほどデプロイした時刻と一致しているか確認

### 未認証アクセスが許可されているか確認

1. Cloud Runサービスの詳細ページで「**権限**」タブ（または「**アクセス**」セクション）を開く
2. プリンシパル一覧に「**allUsers**」が表示されているか確認
3. ロールが「**Cloud Run 起動元**」になっているか確認

**注意**: 権限タブが見つからない場合でも、コマンドで正しく設定されていれば動作します。

---

## 3. 実際にURLにアクセスして確認（最も確実）

デプロイが成功していれば、以下のURLにアクセスして動作確認：

**https://gym-reserve-app-1094873497912.asia-northeast1.run.app/**

### 正常な場合
- ページが表示される
- Forbiddenエラーが表示されない
- ログインページまたはメインページが表示される

### まだForbiddenエラーが出る場合

以下のいずれかを試してください：

#### 方法A: デプロイを再実行

GitHub Actionsでデプロイを再実行する：

1. GitHubリポジトリ → 「Actions」タブ
2. 最新のワークフロー実行をクリック
3. 右上の「**Re-run jobs**」→「**Re-run all jobs**」をクリック

#### 方法B: コマンドで直接権限を設定

もしローカルにgcloudがインストールされていれば：

```bash
gcloud run services add-iam-policy-binding gym-reserve-app \
  --region=asia-northeast1 \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=gym-reserve-app
```

---

## 4. デプロイログに表示される可能性のあるメッセージ

gcloudコマンドのバージョンや設定によって、以下のようなメッセージが表示される可能性があります：

- `Service [gym-reserve-app] revision [xxx] has been deployed`
- `Service URL: https://gym-reserve-app-xxx.run.app`
- `✓ Deploying...`
- `✓ Setting IAM policy...`
- `Allowing unauthenticated invocations`

ただし、これらのメッセージが表示されなくても、デプロイが成功している可能性があります。

---

## トラブルシューティング

### デプロイが失敗している場合

GitHub Actionsのログにエラーが表示されているはずです。エラーメッセージを確認してください。

### デプロイは成功しているが、Forbiddenエラーが出る場合

1. デプロイ後、数秒から数分待つ（設定の反映に時間がかかることがあります）
2. ブラウザのキャッシュをクリアして再度アクセス
3. 上記の「方法B: コマンドで直接権限を設定」を試す


