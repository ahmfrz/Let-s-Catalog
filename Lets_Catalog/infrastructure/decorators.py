from functools import wraps
from flask import redirect, url_for, session, request, flash

def user_loggedin(function):
    '''Decorator to check if user is logged in'''
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            return function(*args, **kwargs)
        else:
            flash('You must be logged in to access this page')
            session['last_URL'] = request.url
            return redirect(url_for('home_page.home'))
    return decorated_function