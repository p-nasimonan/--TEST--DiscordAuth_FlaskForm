# Discordで認証してフォームを作れるか検証
## 概要
DiscordのOAuth2を利用して、ユーザー認証を行い、フォームを作成することを目的としています。

なぜFlaskを使うのか？
- 軽量でシンプルなWebフレームワーク
- Pythonはかける人が多い
- Flaskは学習コストが低い

## 目標
- DiscordのOAuth2を利用してユーザー認証を行う
- 認証後、フォームを入力する
- できればGoogledriveやスプレットシートに保存をする


## なぜDiscordのOAuth2を使うのか？
- Googleよりプライバシーに気にしなくていい。メールアドレスを取得しない
- そのままGASで認証するとユーザにも負担が大きい(ログイン方法が複雑)
- Discordのサーバー内のユーザーのみ使えるようにすると、最高のセキュリティが確保できる。


### AI相談独り言フェーズ
できるかわからないこと
- GASを使ってGoogleスプレッドシートに保存する
- DiscordのOAuth2を使ってGoogleスプレッドシートに保存する

これらをflaskで実装できるのか

Flask + Google API + Discord APIでできるらしい

Discord APIって何ができるのか


GoogleAPIの無料枠が意外と小さい

一旦自宅サーバーに処理は保存しといて、GASで随時同期するのが良いかも
とりあえずSQLiteに保存することから始めましょうか...

結論
# Flask + Discord OAuth2 + SQLite + GASでGoogleスプレッドシートに保存

## 🚀 現在の進捗

### ✅ 完了したもの
- [x] 基本的なFlaskフォーム機能
- [x] SQLiteデータベース連携
- [x] フォームバリデーション
- [x] レスポンシブなWebデザイン
- [x] データ保存・表示機能
- [x] Flask-WTF導入（セキュリティ強化）
- [x] 画像アップロード機能
- [x] Discord OAuth2認証実装
- [x] ユーザーID管理（Discord連携）
- [x] 環境変数による設定管理
- [x] セットアップガイド作成

### 🔄 次のステップ
- [ ] GAS同期API作成
- [ ] Googleスプレッドシート連携
- [ ] サーバー限定アクセステスト
- [ ] 本番環境対応

## 📁 プロジェクト構造

```
DiscordAuth_FlaskForm/
├── README.md
├── setup_guide.md           # セットアップガイド（新規）
├── .env.example            # 環境変数サンプル（新規）
├── .env                    # 実際の設定（Git管理対象外）
├── requirements.txt        # requests追加
├── .gitignore             # .env除外追加
├── app.py                 # 環境変数対応
├── forms.py               # Flask-WTFフォーム
├── discord_config.py      # 環境変数から読み込み
├── discord_auth.py        # Discord認証処理（新規）
├── templates/
│   ├── form.html          # Discord認証状態表示
│   ├── success.html
│   └── data.html          # Discord情報表示対応
├── static/css/
│   └── style.css         # Discord認証UI追加
└── data/
    └── form_data.db      # Discord情報カラム追加
```

## 🔑 セットアップ必須項目

### 1. 環境設定
```bash
cp .env.example .env
```

### 2. Discord Developer Portal
- Client ID取得
- Client Secret取得  
- Redirect URI設定: `http://localhost:5001/auth/callback`

### 3. .envファイル編集
```env
SECRET_KEY=your-secret-key
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
```

## 🏃‍♂️ 実行方法

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. アプリケーション起動
```bash
python app.py
```

### 3. ブラウザでアクセス
```
http://localhost:5001
```

## 📊 データベーススキーマ

```sql
submissions (
    id INTEGER PRIMARY KEY,
    discord_user_id TEXT,        -- Discord User ID（一意）
    discord_username TEXT,       -- Discord ユーザー名（@username形式）
    discord_global_name TEXT,    -- Discord 表示名（優先表示）
    discord_avatar TEXT,         -- アバター画像ハッシュ
    name TEXT,                   -- フォーム入力名
    image_filename TEXT,         -- 元ファイル名
    image_path TEXT,             -- 保存パス
    timestamp TEXT,              -- 送信日時
    created_at DATETIME          -- DB作成日時
)
```

## 🛡️ セキュリティ機能

- **環境変数管理**: 機密情報の安全な管理
- **CSRF保護**: Flask-WTFによる自動保護
- **ファイル検証**: 画像ファイルの拡張子・サイズチェック
- **セキュアファイル名**: UUIDによるユニークファイル名
- **サーバー制限**: 特定Discordサーバーのメンバーのみ許可（オプション）

## 🎯 検証完了事項

1. ✅ **Flask基本機能**: フォーム・DB・テンプレート
2. ✅ **Discord認証**: OAuth2フロー・ユーザー情報取得
3. ✅ **ファイルアップロード**: 安全な画像保存
4. ✅ **環境設定**: 本番対応の設定管理
5. ✅ **UI/UX**: レスポンシブ・認証状態表示

次は GAS同期機能の実装に進めます！