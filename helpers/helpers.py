from functools import wraps
from flask import redirect, url_for, render_template, session

#https://flask.palletsprojects.com/en/2.0.x/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def apology(message, code):
    
    return render_template('apology.html', top=code, bottom=message, hide_header=True), code