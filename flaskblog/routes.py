from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegisterForm, LoginForm, UpdateProfileForm
from flaskblog.models import Post, User

@app.route("/")
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    # If form is valid
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data, rounds=10)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_pw,
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created. You are now logged in!', 'success')
        login_user(new_user, remember=form.remember.data)
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash('Username not found', 'danger')
        else:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)    
                flash('You have been logged in!', 'success')
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('home'))
            else:
                flash('Password did not match', 'danger')
    return render_template('login.html', form=form)


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('profile'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('profile.html', image_file=image_file, form=form)

@login_required
@app.route("/logout")
def logout():
    logout_user()
    flash('You are now logged out', 'success')
    return redirect(url_for('home'))