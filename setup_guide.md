# 🎮 Discord認証フォーム検証プロジェクト

## 📋 セットアップ手順

### 1. リポジトリをクローン
```bash
git clone <リポジトリURL>
cd DiscordAuth_FlaskForm
```

### 2. 環境設定
```bash
# .env.exampleをコピーして.envファイルを作成
cp .env.example .env
```

### 3. Discord Developer Portal設定

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 「New Application」をクリック
3. アプリケーション名を入力（例: "FormTest"）
4. 左サイドバーの「OAuth2」→「General」をクリック
5. **Client ID** と **Client Secret** をコピー
6. **Redirects** に以下を追加:
   ```
   http://localhost:5001/auth/callback
   ```

### 4. .envファイルを編集

```bash
# .envファイルを開いて設定値を入力
vim .env  # または好きなエディタで
```

必須設定項目：
```env
SECRET_KEY=your-super-secret-key-here
DISCORD_CLIENT_ID=あなたのDiscordクライアントID
DISCORD_CLIENT_SECRET=あなたのDiscordクライアントシークレット
```

オプション設定：
```env
# 特定サーバーのメンバーのみ許可する場合
ALLOWED_GUILD_ID=あなたのDiscordサーバーID
```

### 5. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 6. アプリケーション起動
```bash
python app.py
```

### 7. ブラウザでアクセス
```
http://localhost:5001
```

## 🔧 設定オプション

### Discord サーバー制限
特定のDiscordサーバーのメンバーのみアクセス許可したい場合：

1. Discordサーバーで `右クリック` → `サーバーIDをコピー`
2. `.env`ファイルの`ALLOWED_GUILD_ID`に設定

### ポート変更
デフォルトはポート5001です。変更する場合は`app.py`の最終行を編集してください。

## 🗂️ プロジェクト構造

```
DiscordAuth_FlaskForm/
├── README.md                 # このファイル
├── .env.example             # 設定サンプル
├── .env                     # 実際の設定（Git管理対象外）
├── requirements.txt         # 依存関係
├── app.py                   # メインアプリケーション
├── forms.py                 # Flask-WTFフォーム定義
├── discord_config.py        # Discord設定
├── discord_auth.py          # Discord認証処理
├── templates/               # HTMLテンプレート
├── static/                  # CSS、画像
└── data/                    # SQLiteデータベース
```

## 🚀 機能

- ✅ Discord OAuth2認証
- ✅ 画像アップロード機能
- ✅ SQLiteデータベース保存
- ✅ フォームバリデーション
- ✅ レスポンシブデザイン
- ✅ サーバー限定アクセス（オプション）

## 🛡️ セキュリティ

- CSRF保護（Flask-WTF）
- ファイルアップロードのセキュリティチェック
- 環境変数による機密情報管理
- セキュアなファイル名生成

## 📝 TODO

- [ ] GAS同期機能
- [ ] Googleスプレッドシート連携
- [ ] エラーログ機能
- [ ] 管理者パネル

## 🐛 トラブルシューティング

### ポート5000が使用中の場合
macOSのAirPlay Receiverが使用している可能性があります：
`システム設定` → `一般` → `AirDrop & Handoff` → `AirPlay Receiver`をオフ

### Discord認証エラー
1. Client IDとClient Secretが正しく設定されているか確認
2. Redirect URIが正確に設定されているか確認
3. ブラウザのコンソールでエラーメッセージを確認
