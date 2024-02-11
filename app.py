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

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True 
app.config['SESSION_FILE_DIR'] = mkdtemp() #salvar sessão no arquivo temp
app.config['SESSION_PERMANENT'] = False 
app.config['SESSION_TYPE'] = 'filesystem' #sessão será guardada em algum arquivo
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'

Session(app)
db = SQLAlchemy(app)

#definir tabelas sql
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
    task = db.Column(db.String(42), nullable=False)
    description = db.Column(db.String(245))
    start = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ending = db.Column(db.DateTime, nullable=True)

class Request(db.Model):
    __tablename__ = 'requests'
    request_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requested_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Friend(db.Model):
    __tablename__ = 'friends'
    friendship_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)    

#ter certeza de que a tabela existe
with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form.get('username')
        user = request.form.get('user')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
            
        if not user or not password or not confirm_password:
            return apology('Preencha os campos vazios', 403)
        elif not username:
            username = user
        elif password != confirm_password:
            return apology('As senhas devem ser iguais', 403)
        
        if len(user) < 5 or len(user) > 20:
            return apology('usuário precisa ter no mínimo 5 e no máximo 20 dígitos', 403)
        elif len(password) < 10 or len(password) > 20:
            return apology('senha precisa ter no mínimo 10 e no máximo 20 dígitos', 403)
        
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
        return render_template('register.html', hide_header=True)


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
        return render_template('login.html', hide_header=True)


@app.route('/')
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

@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':

        id = session['user_id']

        priority = request.form.get('priority')
        task = request.form.get('task')
        description = request.form.get('description')
        start = request.form.get('start')
        ending = request.form.get('ending')
        print(start)

        if not priority or not task:
            return apology('Precisa ter ao menos a tarefa e a prioridade(Se não tem prioridade você está provavelmente mechendo com o que não deve)', 403)
        if len(description) > 245 or len(task) > 42 or len(task) < 1:
            apology('como você digitou mais/menos que o permitido? está fazendo coisas ilícitas, rapaz?', 403)
        if start:
            start = datetime.strptime(start, '%Y-%m-%dT%H:%M')
        else:                           
            start = datetime.now().strftime('%Y-%m-%dT%H:%M')
            start = datetime.strptime(start, '%Y-%m-%dT%H:%M')
        if ending:
            ending = datetime.strptime(ending, '%Y-%m-%dT%H:%M')
        else:
            ending = None    

        new_task = Task(user_id=id, priority=priority, task=task, description=description, start=start, ending=ending)
        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for('index'))
        

    else:
        priorities = [0,1,2,3]
        return render_template('add_task.html', priorities=priorities)

@app.route('/friends')
@login_required
def friends():

    id = session['user_id']

    friends = []

    user_friends = Friend.query.filter_by(user_id=id).all()

    for user_friend in user_friends:
        friend_info = User.query.filter_by(id=user_friend.friend_id).first()
        if friend_info:
            friends.append({'username':friend_info.username, 'user':friend_info.user, 'id':friend_info.id})

    return render_template('friends.html', friends=friends)

#olhar tabela do amiguinho
@app.route('/see_friend_tasks/<int:friend_id>')
@login_required
def see_friend_task(friend_id):

    id = session['user_id']

    if not id:
        return redirect(url_for('/login'))

    is_friend = Friend.query.filter_by(user_id=id, friend_id=friend_id).first()
    if not is_friend:
        return apology('Ele não é seu amigo ou não existe', 403)
    else:
        friend_tasks = Task.query.filter_by(user_id=friend_id).all()

        friend_user = User.query.filter_by(id=friend_id).first()
        friend_username_info = friend_user.username

        if len(friend_username_info) > 10:
            friend_username = friend_username_info[:10]
        else:
            friend_username = friend_username_info        

        return render_template('see_friend_tasks.html', friend_tasks=friend_tasks, friend_username=friend_username)



@app.route('/add_friend', methods=['GET','POST'])
@login_required
def add_friend():

    id = session['user_id']
 
    if request.method == 'POST':
        
        requested_id = request.form.get('requested_id')

        if not requested_id:
            return apology('Está a tentar enviar pedido para o vazio?', 403) 
        
        user_requested = User.query.filter_by(id=requested_id).first()
        friend_request = Request.query.filter_by(user_id=id, requested_id=requested_id).first()
        received_request = Request.query.filter_by(user_id=requested_id, requested_id=id).first()

        #no caso de não existir
        if not user_requested:
            return apology('esse usuário não existe', 403)
        elif int(requested_id) == int(id):
            return apology('Está tentando enviar um pedido para você mesmo?', 403)
        #no caso de enviar mais de uma vez
        elif friend_request:
            return redirect(url_for('add_friend'))
        #no caso de já ter recebido uma solicitação da pessoa que enviou
        elif received_request:
            already_friends = Friend.query.filter_by(user_id=id, friend_id=requested_id).first()
            if already_friends:
                return apology('Vocês já são amigos', 403)
            else:
                db.session.delete(received_request)
                new_friend = Friend(user_id=id, friend_id=requested_id)
                db.session.add(new_friend)
                db.session.commit()
                new_friend = Friend(user_id=requested_id, friend_id=id)
                db.session.add(new_friend)
                db.session.commit()
        else:
            already_friends = Friend.query.filter_by(user_id=id, friend_id=requested_id).first()
            if already_friends:
                return apology('Vocês já são amigos', 403)
            else:
                new_request = Request(user_id=id, requested_id=requested_id)
                db.session.add(new_request)
                db.session.commit()

        return redirect(url_for('add_friend'))
    else:
        #tabela que contém usuários que enviaram pedido
        requests = []
        requests_ids = Request.query.filter_by(requested_id=id).all()
        for reques in requests_ids:
            user = User.query.filter_by(id=reques.user_id).first()
            if user:
                requests.append({'username':user.username, 'user': user.user, 'id':user.id})       

        return render_template('add_friend.html', user_id=id, requests=requests)

#aceitar solicitação de amizade
@app.route('/accept_friend_request/<int:request_id>')
@login_required
def accept_friend_request(request_id):

    id = session['user_id']

    request =  Request.query.filter_by(user_id=request_id, requested_id=id).first()
    db.session.delete(request)
    db.session.commit()

    new_friend = Friend(user_id=id, friend_id=request_id)
    db.session.add(new_friend)
    db.session.commit()
    new_friend = Friend(user_id=request_id, friend_id=id)
    db.session.add(new_friend)
    db.session.commit()

    return redirect(url_for('add_friend'))

#recusar solicitação de amizade
@app.route('/reject_friend_request/<int:request_id>')
@login_required
def reject_friend_request(request_id):

    id = session['user_id']
    
    request =  Request.query.filter_by(user_id=request_id, requested_id=id).first()
    db.session.delete(request)
    db.session.commit()
    return redirect(url_for('add_friend'))

@app.route('/configs')
@login_required
def configs():

    id = session['user_id']

    user = User.query.filter_by(id=id).first()

    return render_template('configs.html', user=user)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():

    id = session['user_id']

    if request.method == 'POST':
        
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')

        if not old_password or not new_password or not confirm_new_password:
            return apology('preencha os campos vazios', 403)
        elif new_password != confirm_new_password:
            return apology('a senha de confirmação e a nova senha estão diferentes', 403)
        
        user_info = User.query.filter_by(id=id).first()

        if not user_info or not check_password_hash(user_info.hashed_password, old_password):
            return apology('Credenciais inválias', 403)
        
        new_hashed_password = generate_password_hash(new_password)

        user_info.hashed_password = new_hashed_password
        db.session.commit()

        return redirect(url_for('configs'))

    else:
        return render_template('change_password.html', hide_header=True)

#Para erros de servidor: Made by chatgpt3.5
for code, exception in default_exceptions.items():
    app.register_error_handler(exception, lambda e: apology(str(e), code))

@app.errorhandler(403)
def handle_403_error(error):
    return apology('Credenciais inválidas', 403)

if __name__ == '__main__':
    app.run()