# 画面遷移図

## トレーニー（顧客）向け画面遷移

```mermaid
graph TD
    Start([開始]) --> Login[ログイン/新規登録画面]
    Login -->|ログイン成功| Home[予約一覧/カレンダー画面]
    
    Home -->|プラン購入| PlanPurchase[プラン購入画面]
    PlanPurchase -->|プラン選択| Payment[決済画面]
    Payment -->|Stripe決済| PaymentComplete[決済完了画面]
    PaymentComplete -->|戻る| Home
    
    Home -->|予約作成| ReservationNew[予約作成画面]
    ReservationNew -->|プラン未所有| PlanPurchase
    ReservationNew -->|プラン選択・メニュー選択・日時選択| ReservationConfirm[予約確認]
    ReservationConfirm -->|予約確定| Home
    
    Home -->|マイページ| MyPage[マイページ]
    MyPage -->|個人情報編集| UserEdit[個人情報編集]
    UserEdit -->|保存| MyPage
    MyPage -->|プラン購入| PlanPurchase
    MyPage -->|予約履歴| MyReservations[マイ予約一覧画面]
    MyPage -->|カルテ履歴| Charts[カルテ閲覧画面]
    MyPage -->|決済履歴| PaymentHistory[決済履歴画面]
    
    MyReservations -->|予約詳細| ReservationDetail[予約詳細]
    MyReservations -->|キャンセル| ReservationCancel[予約キャンセル確認]
    ReservationCancel -->|確定| MyReservations
    
    Charts -->|カルテ詳細| ChartDetail[カルテ詳細]
    
    style Start fill:#e1f5ff
    style Login fill:#fff4e1
    style Home fill:#e8f5e9
    style PlanPurchase fill:#fff9c4
    style Payment fill:#ffcdd2
    style PaymentComplete fill:#c8e6c9
    style ReservationNew fill:#e1bee7
    style MyPage fill:#b3e5fc
    style MyReservations fill:#b3e5fc
    style Charts fill:#b3e5fc
    style PaymentHistory fill:#b3e5fc
```

## トレーナー向け画面遷移

```mermaid
graph TD
    Start([開始]) --> TrainerLogin[トレーナーログイン画面]
    TrainerLogin -->|ログイン成功| Dashboard[予約管理画面<br/>ダッシュボード]
    
    Dashboard -->|予約選択| ReservationDetail[予約詳細画面]
    ReservationDetail -->|カルテ記録| ChartNew[カルテ記録画面]
    ChartNew -->|保存| ReservationDetail
    ReservationDetail -->|戻る| Dashboard
    
    Dashboard -->|顧客管理| Customers[顧客管理画面]
    Customers -->|顧客選択| CustomerDetail[顧客詳細]
    CustomerDetail -->|予約履歴| CustomerReservations[顧客の予約一覧]
    CustomerDetail -->|カルテ履歴| CustomerCharts[顧客のカルテ一覧]
    CustomerDetail -->|戻る| Customers
    
    Dashboard -->|プラン管理| Plans[プラン管理画面]
    Plans -->|プラン作成| PlanCreate[プラン作成]
    Plans -->|プラン編集| PlanEdit[プラン編集]
    PlanCreate -->|保存| Plans
    PlanEdit -->|保存| Plans
    
    Dashboard -->|メニュー管理| Menus[メニュー管理画面]
    Menus -->|メニュー作成| MenuCreate[メニュー作成]
    Menus -->|メニュー編集| MenuEdit[メニュー編集]
    MenuCreate -->|保存| Menus
    MenuEdit -->|保存| Menus
    
    Dashboard -->|決済管理| Payments[決済管理画面]
    Payments -->|決済詳細| PaymentDetail[決済詳細]
    PaymentDetail -->|戻る| Payments
    
    Dashboard -->|カルテ編集| ChartEdit[カルテ編集画面]
    ChartEdit -->|保存| Dashboard
    ChartEdit -->|削除| Dashboard
    
    style Start fill:#e1f5ff
    style TrainerLogin fill:#fff4e1
    style Dashboard fill:#e8f5e9
    style ReservationDetail fill:#e1bee7
    style ChartNew fill:#c5cae9
    style Customers fill:#b3e5fc
    style Plans fill:#fff9c4
    style Menus fill:#fff9c4
    style Payments fill:#ffcdd2
```

## 主要なユーザーフロー

### フロー1: プラン購入から予約まで

```mermaid
sequenceDiagram
    participant T as トレーニー
    participant UI as 画面
    participant API as バックエンドAPI
    participant S as Stripe
    participant DB as Firestore
    
    T->>UI: プラン購入画面へ
    UI->>API: GET /api/plans
    API->>DB: プラン一覧取得
    DB-->>API: プラン一覧
    API-->>UI: プラン一覧
    UI-->>T: プラン選択
    
    T->>UI: プラン選択・決済画面へ
    UI->>API: POST /api/payments/intent
    API->>S: Payment Intent作成
    S-->>API: Payment Intent ID
    API-->>UI: Payment Intent情報
    UI->>S: Stripe決済処理
    S-->>UI: 決済完了
    
    S->>API: Webhook (payment_intent.succeeded)
    API->>DB: 決済記録・プラン有効化
    DB-->>API: 完了
    API-->>UI: 決済完了通知
    UI-->>T: 決済完了画面
    
    T->>UI: 予約作成画面へ
    UI->>API: GET /api/user-plans
    API->>DB: ユーザープラン取得
    DB-->>API: ユーザープラン
    API-->>UI: ユーザープラン（残り回数）
    UI-->>T: プラン選択・メニュー選択
    
    T->>UI: 予約確定
    UI->>API: POST /api/reservations
    API->>DB: 予約作成・残り回数減算
    DB-->>API: 予約情報
    API-->>UI: 予約完了
    UI-->>T: 予約完了表示
```

### フロー2: カルテ記録

```mermaid
sequenceDiagram
    participant Tr as トレーナー
    participant UI as 画面
    participant API as バックエンドAPI
    participant DB as Firestore
    
    Tr->>UI: 予約管理画面
    UI->>API: GET /api/reservations?trainerId=xxx
    API->>DB: 予約一覧取得
    DB-->>API: 予約一覧
    API-->>UI: 予約一覧
    UI-->>Tr: 予約一覧表示
    
    Tr->>UI: 予約選択・カルテ記録画面へ
    UI->>API: GET /api/reservations/:id
    API->>DB: 予約詳細取得
    DB-->>API: 予約詳細
    API-->>UI: 予約詳細
    UI-->>Tr: カルテ入力フォーム
    
    Tr->>UI: カルテ入力（大カテゴリ・中カテゴリ・備考）
    UI->>API: POST /api/charts
    API->>DB: カルテ保存
    DB-->>API: カルテ情報
    API-->>UI: カルテ保存完了
    UI-->>Tr: カルテ保存完了表示
```

### フロー3: 予約キャンセル

```mermaid
sequenceDiagram
    participant T as トレーニー
    participant UI as 画面
    participant API as バックエンドAPI
    participant DB as Firestore
    
    T->>UI: マイ予約一覧画面
    UI->>API: GET /api/reservations?userId=xxx
    API->>DB: 予約一覧取得
    DB-->>API: 予約一覧
    API-->>UI: 予約一覧
    UI-->>T: 予約一覧表示
    
    T->>UI: キャンセルボタンクリック
    UI-->>T: キャンセル確認ダイアログ
    
    T->>UI: キャンセル確定
    UI->>API: DELETE /api/reservations/:id
    API->>DB: 予約ステータス更新（cancelled）<br/>残り回数戻す
    DB-->>API: 更新完了
    API-->>UI: キャンセル完了
    UI->>API: GET /api/reservations?userId=xxx
    API->>DB: 予約一覧再取得
    DB-->>API: 更新された予約一覧
    API-->>UI: 予約一覧
    UI-->>T: 更新された予約一覧表示
```

## 画面一覧（URLマッピング）

### トレーニー向け
- `/login.html` - ログイン/新規登録画面
- `/` または `/index.html` - 予約一覧/カレンダー画面
- `/reservation/new` - 予約作成画面
- `/mypage` - マイページ
- `/my-reservations` - マイ予約一覧画面
- `/charts` - カルテ閲覧画面
- `/plans/purchase` - プラン購入画面
- `/payment` - 決済画面
- `/payment/complete` - 決済完了画面
- `/payment/history` - 決済履歴画面

### トレーナー向け
- `/trainer/login` - トレーナーログイン画面
- `/trainer/dashboard` - 予約管理画面（ダッシュボード）
- `/trainer/reservations/:id` - 予約詳細画面
- `/trainer/charts/new` - カルテ記録画面
- `/trainer/charts/:id/edit` - カルテ編集画面
- `/trainer/customers` - 顧客管理画面
- `/trainer/customers/:id` - 顧客詳細画面
- `/trainer/plans` - プラン管理画面
- `/trainer/menus` - メニュー管理画面
- `/trainer/payments` - 決済管理画面

