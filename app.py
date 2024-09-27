from flask import Flask, render_template, session
from flask_session import Session
from configs.config import Config
from werkzeug.exceptions import default_exceptions
from helpers.helpers import login_required, apology
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)

Session(app)
db = SQLAlchemy(app)

from routes.account import bp as account_bp
from routes.friends import bp as friends_bp
from routes.tasks import bp as tasks_bp

# Registrar os blueprints
app.register_blueprint(account_bp)
app.register_blueprint(friends_bp)
app.register_blueprint(tasks_bp)

from models import *

#ter certeza de que a tabela existe
with app.app_context():
    db.create_all()

@app.route('/', endpoint='index')
@login_required
def index():

    id = session['user_id']

    tasks = tasks = Task.query.filter_by(user_id=id).all()

    if tasks:
        for task in tasks:
            task.start = task.start.strftime('%d/%m/%y %H:%M')

            if task.ending:
                task.ending = task.ending.strftime('%d/%m/%y %H:%M')
            else:
                task.ending = ' '


    return render_template('index.html', tasks=tasks)

#Para erros de servidor: Made by chatgpt3.5
for code, exception in default_exceptions.items():
    app.register_error_handler(exception, lambda e: apology(str(e), code))

@app.errorhandler(403)
def handle_403_error(error):
    return apology('Credenciais inválidas', 403)

if __name__ == '__main__':
    app.run(debug=True)