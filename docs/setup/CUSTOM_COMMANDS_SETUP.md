# Claude Code カスタムコマンド設定

このドキュメントでは、記事「[CursorとClaude Codeを組み合わせた個人的おすすめAI駆動開発の手順](https://dev.classmethod.jp/articles/cursor-claude-code-ai-driven/)」を参考に、プロジェクトで使用するカスタムコマンドの設定について説明します。

## カスタムコマンドの場所

カスタムコマンドは以下のディレクトリに配置されています：

```
~/.claude/commands/github/
```

## 利用可能なカスタムコマンド

### 1. `/github:issue-from-request`

Issueを作成するコマンドです。

**使用方法：**
```
/github:issue-from-request "issueのタイトルや説明"
```

**例：**
```
/github:issue-from-request "Cloud RunのForbiddenエラーを修正する"
```

### 2. `/github:branch-create`

Issue番号を指定してブランチを作成するコマンドです。

**使用方法：**
```
/github:branch-create {issue番号}
```

**例：**
```
/github:branch-create 1
```

ブランチ名の命名規則：
- 機能追加: `feature/{issue番号}-{説明}`
- バグ修正: `fix/{issue番号}-{説明}`
- リファクタリング: `refactor/{issue番号}-{説明}`

### 3. `/github:pull-request-create`

現在のブランチからプルリクエストを作成するコマンドです。

**使用方法：**
```
/github:pull-request-create "PRの説明（省略可）"
```

**例：**
```
/github:pull-request-create "Cloud Runの未認証アクセス許可機能を追加"
```

### 4. `/github:pull-request-review`

指定されたプルリクエストをレビューするコマンドです。

**使用方法：**
```
/github:pull-request-review {PR番号}
```

**例：**
```
/github:pull-request-review 1
```

レビュー観点：
- コードの品質
- 機能性
- セキュリティ
- テスト
- ドキュメント

### 5. `/github:commit-create`

現在の変更をコミットするコマンドです。

**使用方法：**
```
/github:commit-create "コミットメッセージ（省略可）"
```

**例：**
```
/github:commit-create "fix: Cloud Runの未認証アクセス許可を追加"
```

コミットメッセージの形式：
- `feat`: 新機能の追加
- `fix`: バグ修正
- `refactor`: リファクタリング
- `docs`: ドキュメントの変更
- `style`: コードスタイルの変更
- `test`: テストの追加・変更
- `chore`: ビルドやツールの変更

## 開発フロー例

### 1. 要求整理

```bash
/github:issue-from-request "新機能の追加要求"
```

### 2. 初版作成

```bash
# ブランチ作成
/github:branch-create 1

# CursorでPlanを作成し、Buildを実行
# （手動でデプロイ・動作確認）

# コミット作成
/github:commit-create "feat: 新機能を追加"

# プルリクエスト作成
/github:pull-request-create "新機能の実装"
```

### 3. レビュー対応

```bash
# レビュー実施
/github:pull-request-review 1

# レビュー対応のためのPlan作成・Build実行
# （手動で再デプロイ・動作確認）

# コミット作成
/github:commit-create "fix: レビュー指摘事項の対応"

# 再レビュー
/github:pull-request-review 1
```

## 参考記事

- [CursorとClaude Codeを組み合わせた個人的おすすめAI駆動開発の手順](https://dev.classmethod.jp/articles/cursor-claude-code-ai-driven/)


