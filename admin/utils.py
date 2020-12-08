from cycloan.settings import SECRET_KEY
from django.contrib import messages
from django.shortcuts import redirect

from datetime import datetime, timedelta
import jwt


def verify_auth_token(func):
    @wraps(func)
    def wrapped(self, request, *args, **kwargs):
        auth_token = request.session.get('auth_token')
        if not auth_token:
            messages.warning(request, 'Session expired. Please log in again.')
            return redirect('index-view')
        
        try:
            auth_data = jwt.decode(auth_token, SECRET_KEY, algorithms=['HS256'])
        except:
            messages.warning(request, 'Session expired. Please log in again.')
            return redirect('index-view')
        return func(self, request, *args, **kwargs)

    return wrapped


def create_auth_token(user_id):
    auth_token = jwt.encode(
        {
            'user_id': user_id,
            'exp': datetime.now() + timedelta(seconds=600000)
        }, SECRET_KEY, algorithm='HS256'
    ).decode('utf-8')
    return auth_token


def check_admin(func):
    @wraps(func)
    def wrapped(self, request, *args, **kwargs):
        
        if request.session.get('user_type') == 'admin':
            return redirect('http-403-view')

        return func(self, request, *args, **kwargs)
    return wrapped
