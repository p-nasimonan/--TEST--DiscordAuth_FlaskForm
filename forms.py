from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class ProfileForm(FlaskForm):
    """プロフィールフォーム"""
    name = StringField(
        'お名前', 
        validators=[
            DataRequired(message='お名前は必須です'),
            Length(min=1, max=50, message='お名前は1〜50文字で入力してください')
        ]
    )
    
    image = FileField(
        '画像をアップロード',
        validators=[
            FileRequired(message='画像ファイルを選択してください'),
            FileAllowed(['jpg', 'jpeg', 'png', 'gif'], message='JPG、PNG、GIF形式のファイルのみアップロード可能です')
        ]
    )
    
    submit = SubmitField('送信')
