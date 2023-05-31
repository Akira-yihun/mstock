from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('电子邮箱-Email', validators = [DataRequired(), Length(1, 64), Email(message = '请输入合法的电子邮件地址')])
    #username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('密码-Password', validators = [DataRequired()])
    remember_me = BooleanField('保持登录')
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    email = StringField('电子邮箱-Email', validators = [DataRequired(), Length(1, 64), Email(message = '请输入合法的电子邮件地址')])
    username = StringField('用户名-Username', validators = [
        DataRequired(), Length(4,15), 
        Regexp('^[^\\\/\&\^\|\*\%\'\"\~\`\@\#\$<>:;\{\}\[\]\(\)]{4,15}$', 0, '用户名不能包含特殊字符')])
    password = PasswordField('密码-Password', validators = [
        DataRequired(), EqualTo('passwordcon', '两次输入的密码必须相同'),
        Regexp('^\w{8,20}$', 0, '密码只能包括英文字母、数字和下划线，长度8-20位')])
    passwordcon = PasswordField('验证您的密码', validators = [DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email = field.data).first():
            raise ValidationError('这个电子邮箱已经注册过了')
    
    def validate_username(self, field):
        if User.query.filter_by(username = field.data).first():
            raise ValidationError('这个用户名已经被占用了')


class ChangePasswordForm(FlaskForm):
    pass


class ResetPasswordRequestForm(FlaskForm):
    pass


class ResetPasswordForm(FlaskForm):
    pass


class ChangeEmailForm(FlaskForm):
    pass