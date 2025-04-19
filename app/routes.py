from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import (
    LoginForm,
    RegistrationForm,
    EditProfileForm,
    EmptyForm,
    PostForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
)
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _
import sqlalchemy as sa
from urllib.parse import urlsplit
from datetime import datetime, timezone
from app.models import User, Post
from app.email import send_password_reset_email


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_("Your post is posted :)"))
        return redirect(url_for("index"))

    page = request.args.get("page", 1, int)
    posts = db.paginate(
        current_user.following_posts(),
        page=page,
        per_page=app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    # iterating over the posts (Paginate object) is the same as iterating over posts.items (the actual Post list)
    prev_url = url_for("index", page=posts.prev_num) if posts.has_prev else None
    next_url = url_for("index", page=posts.next_num) if posts.has_next else None
    return render_template(
        "index.html",
        title=_("Home"),
        form=form,
        posts=posts,
        prev_url=prev_url,
        next_url=next_url,
    )


@app.route("/explore")
@login_required
def explore():
    page = request.args.get("page", 1, int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(
        query, page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False
    )
    prev_url = url_for("explore", page=posts.prev_num) if posts.has_prev else None
    next_url = url_for("explore", page=posts.next_num) if posts.has_next else None
    return render_template(
        "index.html", title=_("Explore"), posts=posts, prev_url=prev_url, next_url=next_url
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():  # only called when POSTing the form in the page
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid username or password"))
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title=_("Sign in"), form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_("Congratulations, you are now a registered user!"))
        return redirect(url_for("login"))
    return render_template("register.html", title=_("Register"), form=form)


@app.route("/user/<username>")
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get(key="page", default=1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(
        query, page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False
    )
    prev_url = (
        url_for("user", username=username, page=posts.prev_num)
        if posts.has_prev
        else None
    )
    next_url = (
        url_for("user", username=username, page=posts.next_num)
        if posts.has_next
        else None
    )

    form = EmptyForm()
    return render_template(
        "user.html",
        title=_("Profile"),
        user=user,
        posts=posts,
        form=form,
        prev_url=prev_url,
        next_url=next_url,
    )


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_("Changes saved."))
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title=_("Edit profile"), form=form)


@app.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == username))
        if user is None:
            flash(_("User not found!"))
            return redirect(url_for("index"))
        if user == current_user:
            flash(_("You cannot follow yourself!"))
            return redirect(url_for("user", username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_("You're following %(username)s.", username=user.username))
        return redirect(url_for("user", username=username))

    else:
        return redirect(url_for("index"))


@app.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == username))
        if user is None:
            flash(_("User not found!"))
            return redirect(url_for("index"))
        if user == current_user:
            flash(_("You cannot unfollow yourself!"))
            return redirect(url_for("user", username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_("You are not following %(username)s anymore.", username=user.username))
        return redirect(url_for("user", username=username))

    else:
        return redirect(url_for("index"))


@app.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        query = sa.Select(User).where(User.email == form.email.data)
        user = db.session.scalar(query)
        if user:
            send_password_reset_email(user)
        flash(_("Check your emails for the instructions to reset your password"))
        return redirect(url_for("login"))

    return render_template(
        "reset_password_request.html", title=_("Reset password"), form=form
    )


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.verify_reset_password_token(token)
        if not user:
            return redirect(url_for("index"))
        user.set_password(form.password.data)
        db.session.commit()
        flash(_("Password reset!"))
        return redirect(url_for("login"))

    return render_template("reset_password.html", title=_("Set new password"), form=form)
