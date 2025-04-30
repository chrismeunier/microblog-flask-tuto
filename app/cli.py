from flask import Blueprint
import os
import click

bp = Blueprint("cli", __name__, cli_group=None)

def babel_extract():
    if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
        raise RuntimeError("extract command failed")


def babel_cleanup():
    os.remove("messages.pot")


@bp.cli.group()
def translate():
    """Translation commands:
    Adding `flask translate init [LANG]`, `flask translate update` and `flask translate compile`
    """
    pass


@translate.command()
@click.argument("lang")
def init(lang):
    """Initialize a new language"""
    babel_extract()
    if os.system(f"pybabel init -i messages.pot -d app/translations -l {lang}"):
        raise RuntimeError("init command failed")
    babel_cleanup()


@translate.command()
def update():
    """Update all languages"""
    babel_extract()
    if os.system("pybabel update -i messages.pot -d app/translations"):
        raise RuntimeError("update command failed")
    babel_cleanup()


@translate.command()
def compile():
    """Compile all translations"""
    if os.system("pybabel compile -d app/translations"):
        raise RuntimeError("compile command failed")
