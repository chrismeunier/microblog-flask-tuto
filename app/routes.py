from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

@app.route("/")
@app.route("/index")
def index():
    user = {"username": "Christophe"}
    posts = [
        {"author": {"username": "Charlotte"}, "body": "It's a beautiful day!"},
        {"author": {"username": "Clément"}, "body": "I am very smart."},
        {"author": {"username": "Plup"}, "body": "Anyone want a drink?"},
    ]
    return render_template("index.html", title="Home", user=user, posts=posts)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit(): # only called when POSTing the form in the page
        flash("Login requested for user {}, remember={}".format(form.username.data, form.remember_me.data))
        return redirect(url_for("index"))
    return render_template("login.html", title="Sign in", form=form)