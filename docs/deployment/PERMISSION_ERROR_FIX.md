# IAMポリシー設定エラーの対処方法

## エラー内容

```
ERROR: (gcloud.run.services.add-iam-policy-binding) FAILED_PRECONDITION: 
One or more users named in the policy do not belong to a permitted customer, 
perhaps due to an organization policy.
```

## 原因

このエラーは、組織ポリシー（Organization Policy）によって`allUsers`へのIAMポリシー設定が制限されている可能性があります。

## 解決方法

### 方法1: `--allow-unauthenticated`フラグを使用（推奨・現在適用済み）

`gcloud run deploy`コマンドに`--allow-unauthenticated`フラグを追加することで、デプロイ時に自動的に未認証アクセスが許可されます。

この方法では、`add-iam-policy-binding`コマンドは不要です。

### 方法2: GCPコンソールで直接設定

1. [GCPコンソール](https://console.cloud.google.com/)にアクセス
2. 「Cloud Run」→「gym-reserve-app」サービスを選択
3. サービス詳細ページで、上部の「**アクセスを許可**」または「**Manage access**」ボタンを探す
4. 「**プリンシパルを追加**」をクリック
5. 「**allUsers**」を追加して「**Cloud Run 起動元**」ロールを付与

### 方法3: 組織ポリシーを確認・変更（管理者権限が必要）

組織ポリシーで`allUsers`へのアクセスが制限されている場合、以下のポリシーを確認してください：

1. GCPコンソール → 「IAMと管理」→「組織ポリシー」
2. 「Domain Restricted Sharing」ポリシーを確認
3. 必要に応じて、プロジェクトレベルでこの制限を解除

---

## 現在の設定

ワークフローファイルでは、`gcloud run deploy`コマンドに`--allow-unauthenticated`フラグを使用しています。

このフラグが正しく動作すれば、別途IAMポリシーを設定する必要はありません。

---

## 確認方法

デプロイ後、以下のURLにアクセスして動作確認：

https://gym-reserve-app-1094873497912.asia-northeast1.run.app/

正常にページが表示されれば成功です。


