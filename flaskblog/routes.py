import secrets, os, requests
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegisterForm, LoginForm, UpdateProfileForm, PostForm
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
    url = 'https://api.imgbb.com/1/upload'
    files = {
        'image': form_picture
    }
    params = {
        'key': os.environ['IMBB_KEY']
    }
    res = requests.post(url, params=params, files=files)
    print(res.json())

    return res.json()['data']['url']

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

@app.route("/logout")
@login_required
def logout():
    # Logout user and redirect to home page
    logout_user()
    flash('You are now logged out', 'success')
    return redirect(url_for('home'))

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Post Created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form)

@app.route("/post/<int:id>")
def post(id):
    post = Post.query.get(id)
    if not post:
        abort(404)
    return render_template("post.html", post=post)

@app.route("/post/<int:id>/update", methods=["GET","POST"])
@login_required
def update_post(id):
    post = Post.query.get(id)
    if not post:
        abort(404)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Post has been updated!")
        return redirect(url_for('post', id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content

    return render_template("create_post.html", form=form, title="Update Post")

@app.route("/post/<int:id>/delete", methods=["POST"])
@login_required
def delete_post(id):
    post = Post.query.get(id)
    if not post:
        abort(404)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))