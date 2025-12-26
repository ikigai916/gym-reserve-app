#!/bin/bash

# Cloud Runサービスに未認証アクセスを許可するスクリプト

PROJECT_ID="gym-reserve-app"
SERVICE_NAME="gym-reserve-app"
REGION="asia-northeast1"

echo "Cloud Runサービスに未認証アクセスを許可しています..."
echo "プロジェクト: $PROJECT_ID"
echo "サービス: $SERVICE_NAME"
echo "リージョン: $REGION"
echo ""

gcloud run services add-iam-policy-binding $SERVICE_NAME \
  --region=$REGION \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=$PROJECT_ID

echo ""
echo "設定が完了しました！"
echo "数秒待ってから、以下のURLにアクセスしてください:"
echo "https://gym-reserve-app-1094873497912.asia-northeast1.run.app/"


