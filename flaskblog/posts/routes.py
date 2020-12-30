from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_required
from flaskblog import app, db
from flaskblog.posts.forms import PostForm, CommentForm
from flaskblog.models import Post, Comment, Like
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

@posts.route("/post/<int:id>", methods=["POST", "GET"])
def post(id):
    post = Post.query.get(id)

    if not post:
        abort(404)

    liked = Like.query.filter_by(author=current_user, post=post).first()
    likes = Like.query.filter_by(post=post).count()

    print(likes)

    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You need to login to comment.', 'success')
            return redirect(url_for('login'))

        new_comment = Comment(
            body=comment_form.content.data,
            author=current_user,
            post=post
        )

        db.session.add(new_comment)
        db.session.commit()

    return render_template("post.html", post=post, comment_form=comment_form, liked=liked, likes=likes)

@posts.route("/post/<int:id>/update", methods=["GET","POST"])
@login_required
def update_post(id):
    post = Post.query.get(id)

    if not post:
        abort(404)
    
    if current_user.is_admin != 'True':
        if post.author != current_user:
            abort(403)
    
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Post has been updated!", 'success')
        return redirect(url_for('posts.post', id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content

    return render_template("create_post.html", form=form, title="Update Post")

@posts.route("/post/<int:id>/like", methods=["POST"])
@login_required
def like_post(id):
    post = Post.query.get(id)

    if not post:
        abort(404)
    
    liked = Like.query.filter_by(author=current_user, post=post).first()
    if not liked:
        new_like = Like(
            author = current_user,
            post = post
        )
        db.session.add(new_like)
        db.session.commit()
        flash('Your liked this post', 'success')
        return redirect(url_for('posts.post', id=post.id))

    else:
        db.session.delete(liked)
        db.session.commit()
        flash('Your unliked this post', 'success')
        return redirect(url_for('posts.post', id=post.id))

@posts.route("/post/<int:id>/delete", methods=["POST"])
@login_required
def delete_post(id):
    post = Post.query.get(id)

    if not post:
        abort(404)
    
    if current_user.is_admin != 'True':
        if post.author != current_user:
            abort(403)
    
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('main.home'))

@posts.route("/comment/<int:id>/delete", methods=["POST"])
@login_required
def delete_comment(id):
    comment = Comment.query.get(id)
    if not comment:
        abort(404)
    if comment.author != current_user:
        abort(403)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted', 'success')
    return redirect(url_for('posts.post', id=post_id))