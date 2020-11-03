from django.utils.decorators import wraps
from django.shortcuts import redirect
from django.contrib import messages
from cycloan.settings import SECRET_KEY

from datetime import datetime, timedelta
import jwt


def verify_auth_token(func):
    @wraps(func)
    def wrapped(self, request, *args, **kwargs):
        auth_token = request.session.get('auth_token')
        if not auth_token:
            messages.warning(request, 'Session expired. Please log in again.')
            return redirect('login-view')
        
        try:
            auth_data = jwt.decode(auth_token, SECRET_KEY, algorithms=['HS256'])
        except:
            messages.warning(request, 'Session expired. Please log in again.')
            return redirect('login-view')
        return func(self, request, *args, **kwargs)

    return wrapped


def create_auth_token(user_id):
    auth_token = jwt.encode(
        {
            'user_id': user_id,
            'exp': datetime.now() + timedelta(seconds=600000)
        }, SECRET_KEY, algorithm='HS256'
    ).decode('utf-8')
    print(type(auth_token))
    return auth_token


def check_customer(func):
    @wraps(func)
    def wrapped(self, request, *args, **kwargs):
        
        if request.session.get('user_type') == 'owner':
            messages.warning(request, 'You are not allowed to view that page.')
            return redirect('owner-dashboard-view')

        return func(self, request, *args, **kwargs)
    return wrapped


def check_owner(func):
    @wraps(func)
    def wrapped(self, request, *args, **kwargs):
        
        if request.session.get('user_type') == 'customer':
            messages.warning(request, 'You are not allowed to view that page.')
            return redirect('customer-dashboard-view')

        return func(self, request, *args, **kwargs)
    return wrapped

