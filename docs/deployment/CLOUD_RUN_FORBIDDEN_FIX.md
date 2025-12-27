# Cloud Run「Forbidden」エラーの修正方法

## 問題

Cloud Runにアクセスすると「Error: Forbidden」エラーが表示される。

これは、Cloud Runサービスが認証を要求しているためです。

## 解決方法（2つの方法）

### 方法1: GCPコンソールで設定（すぐに修正できる）

1. [GCPコンソール](https://console.cloud.google.com/)にアクセス
2. 左メニューから「**Cloud Run**」をクリック
3. サービス一覧から「**gym-reserve-app**」をクリック
4. 上部の「**権限**」タブをクリック
5. 「**プリンシパルを追加**」をクリック
6. 以下の設定で追加：
   - **プリンシパル**: `allUsers`
   - **ロール**: `Cloud Run 起動元` (`roles/run.invoker`)
7. 「**保存**」をクリック
8. 確認ダイアログで「**確認**」をクリック

これで、誰でもアクセスできるようになります。

---

### 方法2: ワークフローで自動設定（推奨）

GitHub Actionsのワークフローファイルを修正して、デプロイ時に自動的に未認証アクセスを許可するようにします。

`.github/workflows/deploy.yml` を修正：

```yaml
      - name: 'Deploy to Cloud Run'
        uses: 'google-github-actions/deploy-cloudrun@v2'
        with:
          service: ${{ env.SERVICE_NAME }}
          region: ${{ env.REGION }}
          image: "${{ env.GAR_LOCATION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPOSITORY }}/${{ env.SERVICE_NAME }}:${{ github.sha }}"
          flags: '--allow-unauthenticated'
```

または、gcloudコマンドで直接デプロイする場合：

```yaml
      - name: 'Deploy to Cloud Run'
        run: |-
          gcloud run deploy ${{ env.SERVICE_NAME }} \
            --image "${{ env.GAR_LOCATION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPOSITORY }}/${{ env.SERVICE_NAME }}:${{ github.sha }}" \
            --region ${{ env.REGION }} \
            --platform managed \
            --allow-unauthenticated
```

---

## 確認方法

設定後、以下のURLにアクセスして、正常にページが表示されることを確認：

https://gym-reserve-app-1094873497912.asia-northeast1.run.app/

## セキュリティの注意

- `--allow-unauthenticated` を設定すると、誰でもサービスにアクセスできます
- 本番環境では、必要に応じて認証を有効にすることを検討してください
- ただし、このジム予約システムは公開サービスのため、未認証アクセスは適切です


