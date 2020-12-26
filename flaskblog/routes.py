import secrets
import os
from PIL import Image
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegisterForm, LoginForm, UpdateProfileForm
from flaskblog.models import Post, User

@app.route("/")
def home():
    # Get all posts and render it
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    # If user is logged in then redirect them to home page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    # If they click on register and form is valid
    if form.validate_on_submit():
        # Hash the password create a user and login
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
    # If user is logged in then redirect them to home page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    # If they click on login and form is valid
    if form.validate_on_submit():
        # Check if user exist and if password matched then login
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash('Username not found', 'danger')
        else: # If user found
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)    
                flash('You have been logged in!', 'success')
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('home'))
            else: # If password did not matched
                flash('Password did not match', 'danger')
    return render_template('login.html', form=form)

# Resize and save image to the disk
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)
    return picture_fn

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    # Show profile page and update on POST request
    form = UpdateProfileForm()
    # Get the image path for current user
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    if form.validate_on_submit(): # Update Profile
        if form.picture.data: # If new profile picture is given then update to it
            current_user.image_file = save_picture(form.picture.data)
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('profile'))
    elif request.method == "GET": # Display Profile detail
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('profile.html', image_file=image_file, form=form)

@login_required
@app.route("/logout")
def logout():
    # Logout user and redirect to home page
    logout_user()
    flash('You are now logged out', 'success')
    return redirect(url_for('home'))