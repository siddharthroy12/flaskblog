from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_required
from flaskblog import app, db
from flaskblog.posts.forms import PostForm
from flaskblog.models import Post
from flask import Blueprint

posts = Blueprint('posts', __name__)

@posts.route("/post/new", methods=['GET', 'POST'])
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
        return redirect(url_for('main.home'))
    return render_template('create_post.html', form=form)

@posts.route("/post/<int:id>")
def post(id):
    post = Post.query.get(id)
    if not post:
        abort(404)
    return render_template("post.html", post=post)

@posts.route("/post/<int:id>/update", methods=["GET","POST"])
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
        return redirect(url_for('posts.post', id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content

    return render_template("create_post.html", form=form, title="Update Post")

@posts.route("/post/<int:id>/delete", methods=["POST"])
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
    return redirect(url_for('main.home'))