import secrets, os, requests
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import app, db, bcrypt, email_server
from flaskblog.forms import (
    RegisterForm, LoginForm, UpdateProfileForm,
    PostForm, PasswordResetForm, ForgotPasswordResetForm
)
from flaskblog.models import Post, User
from itsdangerous import TimedJSONWebSignatureSerializer

@app.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
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

@app.route("/user/<string:username>")
def user(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query\
        .filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user.html', posts=posts, user=user)

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

@app.route("/resetpassword/<string:token>", methods=['GET', 'POST'])
def reset_password(token):
    user = None
    if token == "self":
        if current_user.is_authenticated:
            user = current_user
        else:
            abort(401)
    else:
        user = User.verify_reset_token(token)
        if not user:
            abort(401)
    
    form = PasswordResetForm()

    if form.validate_on_submit():
        # Hash the password create a user and login
        hashed_pw = bcrypt.generate_password_hash(form.new_password.data, rounds=10)
        user.password = hashed_pw
        db.session.commit()
        flash('Password reset successfull!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route("/forgotpassword", methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = ForgotPasswordResetForm()

    if form.validate_on_submit():
        s = TimedJSONWebSignatureSerializer(app.config['SECRET_KEY'], 3600)
        user = User.query.filter_by(email=form.email.data).first()
        token = s.dumps({"id": user.id}).decode('utf-8')
        reset_link = request.url_root[:-1] + url_for('reset_password', token=token)

        message = f"""\
        From: {os.environ['EMAIL']}
        To: {form.email.data}
        Subject: Reset Your Password


        Hi {user.username}!
        You can reset your password at {reset_link}

        This link will expire in 1 hour.
        If you haven't requested password reset then you can ignore this mail and don't share this link with anyone
        """

        email_server.sendmail(os.environ['EMAIL'], form.email.data, message)
        
        flash('Reset link sent to your email', 'success')

    return render_template('request_password_reset.html', form=form)
