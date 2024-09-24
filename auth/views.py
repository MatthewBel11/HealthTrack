from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from auth.forms import RegisterForm, LoginForm
from firebase_admin import db

auth_blueprint = Blueprint('auth', __name__, template_folder='templates')


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        # Checks if username exists in the database
        find = db.reference("/Accounts/" + username)
        if find.get() is None:
            flash("Username does not exist")
        else:
            # Checks if password matches the one in the database
            pass_ref = db.reference("/Accounts/" + username + "/password").get()
            if pass_ref == form.password.data:
                session['user'] = username
                return redirect(url_for('account.family'))
            else:
                flash("Login details are incorrect")
                return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@auth_blueprint.route('/sign-up', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        phone = form.phone.data
        password = form.password.data
        # Adds a new account to the database
        ref = db.reference("Accounts/" + username)
        ref.set({
            'email': email,
            'password': password,
            'phone': phone
        })
        return redirect(url_for('auth.login'))
    return render_template('createAccount.html', form=form)

@auth_blueprint.route('/logout', methods=['GET'])
def logout():
    # Clear the session
    session.pop('user', None)
    # Redirect to the sign-up page
    return redirect(url_for('auth.register'))

@auth_blueprint.route('/change-password', methods=['POST'])
def change_password():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:
        flash("New password and confirmation do not match")
        return redirect(url_for('account.settings'))

    user_id = session['user']
    user_ref = db.reference("/Accounts/" + user_id)
    stored_password = user_ref.child('password').get()

    if stored_password != current_password:
        flash("Current password is incorrect")
        return redirect(url_for('account.settings'))

    user_ref.update({'password': new_password})
    flash("Password changed successfully")
    return redirect(url_for('account.settings'))