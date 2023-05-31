from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import auth
from .. import db
from ..models import User

from .forms import LoginForm, RegisterForm


@auth.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.personal_index')
            return redirect(next)
        flash('山回路转不见君，用户名和密码似乎有点问题。')
    return render_template('auth/login.html', form = form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('离离原上草，一岁一枯荣，下次见。')
    return redirect(url_for('main.index'))

@auth.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email = form.email.data,
                    username = form.username.data,
                    password = form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('我欲寻花穿路，直入白云深处，欢迎进入新的世界。')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form = form)

