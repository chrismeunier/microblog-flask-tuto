import os
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(base_dir, ".env"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(base_dir, "app.db")
    POSTS_PER_PAGE = 10
    # To get the "emails" sent when there is an error in a terminal run:
    # aiosmtpd -n -c aiosmtpd.handlers.Debugging -l 127.0.0.1:8025
    # or with whatever address and port the app uses
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = ["noreply.password.reset@aiosmtpd.com", "sysadmin@aiosmtpd.com"]
    LANGUAGES = ["en", "fr"]
    MS_TRANSLATOR_KEY = os.environ.get("MS_TRANSLATOR_KEY")
    MS_TRANSLATOR_LOCATION = os.environ.get("MS_TRANSLATOR_LOCATION")
