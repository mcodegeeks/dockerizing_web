from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from app import db
from app.auth import bp
from app.auth.views import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from app.auth.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Your email does not exist.')
            return redirect(url_for('auth.login'))
        elif not user.validate_password(form.password.data):
            flash('Your password is incorrect.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.rememberMe.data)
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign in', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have been registered successfully. Try signing in with it here.')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Sign up', form=form)


@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("We're sorry. We weren't able to identify you given the information provided.")
            return redirect(url_for('auth.forgot_password'))
        token = user.get_reset_password_token()
        return redirect(url_for('auth.reset_password', token=token))
    return render_template('forgot_password.html', title='Forgot password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.validate_reset_password_token(token)
    if not user:
        return redirect(url_for('auth.forgot_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been changed successfully. Try signing in with it here.')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', title='Reset password', form=form)
