from app import create_app, db
import sqlalchemy as sa
import sqlalchemy.orm as so

# Start the server with `flask run` if `set FLASK_APP=microblog.py`
# or with `flask --app microblog run`

app = create_app()

# To start an interpreter session with the app context:
# `flask shell`
@app.shell_context_processor
def make_shell_context():
    return {"sa": sa, "so": so}
