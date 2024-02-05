import os

from datetime import datetime

from flask import Flask, request, redirect, render_template, url_for, session

#gerenciar sessões
from flask_session import Session
from tempfile import mkdtemp

#Gerenciar senhas
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions

#obrigar a logar 
from helpers import login_required, apology

#gerenciador de database
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True 
app.config['SESSION_FILE_DIR'] = mkdtemp() #salvar sessão no arquivo temp
app.config['SESSION_PERMANENT'] = False 
app.config['SESSION_TYPE'] = 'filesystem' #sessão será guardada em algum arquivo
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'

Session(app)
db = SQLAlchemy(app)

#ter certeza de que a tabela existe


#definir tabela sql
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(20), nullable=False)
    hashed_password = db.Column(db.String(120), nullable=False)

class Task(db.Model):
    __tablename__ = 'tasks'
    task_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    task = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    remaining_time = db.Column(db.String(20), nullable=False)
    start = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ending = db.Column(db.DateTime, nullable=False)


with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form.get('username')
        user = request.form.get('user')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not user or not password or not confirm_password:
            return apology('Preencha os campos vazios', 403)
        elif password != confirm_password:
            return apology('As senhas devem ser iguais', 403)
        
        repeat_user = db.session.query(User).filter_by(user=user).first()
        if repeat_user:
            return apology('Nome já está em uso', 403)

        #geração de senha segura e insersão de conta na database
        hashed_password = generate_password_hash(password)
        new_user = User(user=user, username=username, hashed_password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    session.clear()

    if request.method == 'POST':

        user = request.form.get('user')
        password = request.form.get('password')

        if not user or not password:
            return apology('Preencha os campos vazios', 403)
        
        user_info = User.query.filter_by(user=user).first()

        #checar se usuário existe e se a senha é correta
        if not user_info or not check_password_hash(user_info.hashed_password, password):
            return apology('Credenciais inválidas', 403)

        #acessar usuário que está logado
        session['user_id'] = user_info.id

        return redirect(url_for('index'))
    else:
        return render_template('login.html')


@app.route('/')
@login_required
def index():

    tasks = tasks = Task.query.all()

    return render_template('index.html', tasks=tasks)

@app.route('/friends')
@login_required
def friends():

    return render_template('friends.html')

#Para erros de servidor: Made by chatgpt3.5
for code, exception in default_exceptions.items():
    app.register_error_handler(exception, lambda e: apology(str(e), code))

@app.errorhandler(403)
def handle_403_error(error):
    return apology('Credenciais inválidas', 403)

if __name__ == '__main__':
    app.run()