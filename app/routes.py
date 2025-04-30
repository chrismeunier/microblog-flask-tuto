from flask import render_template, flash, redirect, url_for, request, g
from app import app, db
from app.forms import (
    EditProfileForm,
    EmptyForm,
    PostForm,
)
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import sqlalchemy as sa
from datetime import datetime, timezone
from langdetect import detect, LangDetectException
from app.models import User, Post
from app.translate import translate


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
    g.locale = get_locale()


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ""
        post = Post(body=form.post.data, author=current_user, language=language)
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
        "index.html",
        title=_("Explore"),
        posts=posts,
        prev_url=prev_url,
        next_url=next_url,
    )


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


@app.route("/translate", methods=["POST"])
@login_required
def translate_text():
    data = request.get_json()
    return {
        "text": translate(data["text"], data["source_language"], data["dest_language"])
    }
