"""
Discord OAuth2 認証処理
"""
import os
from flask import session, redirect, request, flash, url_for
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# Discord設定
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:5001/auth/callback')
ALLOWED_GUILD_ID = os.getenv('ALLOWED_GUILD_ID')

# Discord API URL
DISCORD_OAUTH_URL = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_API_BASE = "https://discord.com/api"
DISCORD_SCOPES = ["identify", "guilds"]

def get_discord_auth_url():
    """Discord認証URLを生成"""
    params = {
        'client_id': DISCORD_CLIENT_ID,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(DISCORD_SCOPES)
    }
    return f"{DISCORD_OAUTH_URL}?{urlencode(params)}"

def exchange_code_for_token(code):
    """認証コードをアクセストークンに交換"""
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }
    
    response = requests.post(DISCORD_TOKEN_URL, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"トークン取得エラー: {response.status_code} - {response.text}")
        return None

def get_discord_user(access_token):
    """Discord APIからユーザー情報を取得"""
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # ユーザー情報取得
    user_response = requests.get(f"{DISCORD_API_BASE}/users/@me", headers=headers)
    
    if user_response.status_code == 200:
        user_data = user_response.json()
        
        # サーバー一覧を取得（セッション保存用には加工する）
        guilds_response = requests.get(f"{DISCORD_API_BASE}/users/@me/guilds", headers=headers)
        if guilds_response.status_code == 200:
            full_guilds = guilds_response.json()
            # セッション用には必要最小限の情報のみ保存
            user_data['guild_ids'] = [guild['id'] for guild in full_guilds]
            # 権限チェック用に完全なguilds情報を一時的に保存
            user_data['_temp_guilds'] = full_guilds
        
        return user_data
    else:
        print(f"ユーザー情報取得エラー: {user_response.status_code}")
        return None

def check_guild_membership(user_data, required_guild_id=None):
    """特定のDiscordサーバーのメンバーかチェック"""
    if not required_guild_id:
        return True  # サーバー制限なし
    
    # 一時的なguilds情報を使用してチェック
    guilds = user_data.get('_temp_guilds', [])
    for guild in guilds:
        if guild['id'] == required_guild_id:
            return True
    
    return False

def handle_discord_callback(code):
    """Discord認証コールバック処理"""
    # トークン取得
    token_data = exchange_code_for_token(code)
    if not token_data:
        return False, "認証に失敗しました"
    
    access_token = token_data['access_token']
    
    # ユーザー情報取得
    user_data = get_discord_user(access_token)
    if not user_data:
        return False, "ユーザー情報の取得に失敗しました"
    
    # サーバーメンバーシップチェック（オプション）
    if not check_guild_membership(user_data, ALLOWED_GUILD_ID):
        return False, "このサーバーのメンバーではありません"
    
    # セッション保存前に一時的なデータを削除
    if '_temp_guilds' in user_data:
        del user_data['_temp_guilds']
    
    # セッションに最小限の情報のみ保存
    session['discord_user'] = {
        'id': user_data['id'],
        'username': user_data['username'],
        'discriminator': user_data.get('discriminator', '0'),
        'global_name': user_data.get('global_name'),
        'avatar': user_data.get('avatar'),
        'guild_ids': user_data.get('guild_ids', [])
    }
    # アクセストークンは必要な時のみ保存（今回は不要）
    # session['access_token'] = access_token
    
    return True, f"ようこそ、{user_data.get('global_name') or user_data['username']}さん！"
