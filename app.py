from flask import Flask, render_template, request, redirect, url_for, flash, session
from forms import ProfileForm
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
from discord_auth import get_discord_auth_url, handle_discord_callback

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB max-limit

# データベース初期化
def init_db():
    """SQLiteデータベースを初期化"""
    os.makedirs('data', exist_ok=True)
    
    database_path = os.getenv('DATABASE_PATH', 'data/form_data.db')
    conn = sqlite3.connect(database_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_user_id TEXT,
            discord_username TEXT,
            discord_global_name TEXT,
            discord_avatar TEXT,
            name TEXT NOT NULL,
            image_filename TEXT NOT NULL,
            image_path TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("データベースを初期化しました")

def save_form_data(name, image_filename, image_path, discord_user=None):
    """フォームデータをデータベースに保存"""
    database_path = os.getenv('DATABASE_PATH', 'data/form_data.db')
    conn = sqlite3.connect(database_path)
    
    if discord_user:
        # Discord認証済みの場合
        conn.execute('''
            INSERT INTO submissions (discord_user_id, discord_username, discord_global_name, 
                                   discord_avatar, name, image_filename, image_path, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            discord_user.get('id'),
            discord_user.get('username'),
            discord_user.get('global_name'),
            discord_user.get('avatar'),
            name, 
            image_filename, 
            image_path, 
            datetime.now().isoformat()
        ))
    else:
        # Discord認証なしの場合（現在の状態）
        conn.execute('''
            INSERT INTO submissions (name, image_filename, image_path, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (name, image_filename, image_path, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def allowed_file(filename):
    """ファイル拡張子チェック"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """アップロードされたファイルを保存"""
    if file and allowed_file(file.filename):
        # ファイル名をセキュアにして、ユニークにする
        original_filename = secure_filename(file.filename)
        filename_ext = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{filename_ext}"
        
        # ファイルパス生成
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # ディレクトリ作成
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # ファイル保存
        file.save(file_path)
        
        return original_filename, file_path
    return None, None

@app.route('/')
def index():
    """メインページ（認証チェック）"""
    # Discord認証状態をチェック
    if 'discord_user' in session:
        # 認証済み → フォームページへ
        return redirect(url_for('form_page'))
    else:
        # 未認証 → ログインページへ
        return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    """ログインページ"""
    # 既に認証済みの場合はフォームへリダイレクト
    if 'discord_user' in session:
        return redirect(url_for('form_page'))
    
    return render_template('login.html')

@app.route('/form', methods=['GET', 'POST'])
def form_page():
    """フォームページ（認証必須）"""
    # 認証チェック
    if 'discord_user' not in session:
        flash('フォームにアクセスするにはDiscord認証が必要です', 'error')
        return redirect(url_for('login_page'))
    
    form = ProfileForm()
    
    if form.validate_on_submit():
        # フォームデータを取得
        name = form.name.data.strip() if form.name.data else ''
        image_file = form.image.data
        
        # 画像ファイルを保存
        original_filename, file_path = save_uploaded_file(image_file)
        
        if original_filename and file_path:
            # セッションからDiscordユーザー情報を取得
            discord_user = session.get('discord_user')
            
            # データベースに保存
            try:
                save_form_data(name, original_filename, file_path, discord_user)
                flash('プロフィールが正常に送信されました！', 'success')
                return redirect(url_for('success'))
            except Exception as e:
                flash('エラーが発生しました。もう一度お試しください。', 'error')
                print(f"エラー: {e}")
        else:
            flash('画像ファイルの保存に失敗しました。', 'error')
    
    return render_template('form.html', form=form)

@app.route('/success')
def success():
    """送信成功ページ"""
    return render_template('success.html')

@app.route('/data')
def view_data():
    """保存されたデータを表示（管理用）"""
    database_path = os.getenv('DATABASE_PATH', 'data/form_data.db')
    conn = sqlite3.connect(database_path)
    cursor = conn.execute('SELECT * FROM submissions ORDER BY created_at DESC')
    submissions = cursor.fetchall()
    conn.close()
    
    return render_template('data.html', submissions=submissions)

@app.route('/auth/login')
def discord_login():
    """Discord認証開始"""
    auth_url = get_discord_auth_url()
    return redirect(auth_url)

@app.route('/auth/callback')
def discord_callback():
    """Discord認証コールバック"""
    code = request.args.get('code')
    
    if not code:
        flash('認証がキャンセルされました', 'error')
        return redirect(url_for('login_page'))
    
    success, message = handle_discord_callback(code)
    
    if success:
        flash(message, 'success')
        return redirect(url_for('form_page'))  # 認証成功後はフォームへ
    else:
        flash(message, 'error')
        return redirect(url_for('login_page'))  # 認証失敗時はログインへ

@app.route('/auth/logout')
def discord_logout():
    """Discord認証をログアウト"""
    session.pop('discord_user', None)
    # session.pop('access_token', None)  # 保存していないので不要
    flash('ログアウトしました', 'success')
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    init_db()
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5001)
