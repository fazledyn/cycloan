from django.utils.decorators import wraps
from cycloan.settings import SECRET_KEY
from django.contrib import messages
from django.shortcuts import redirect

from datetime import datetime, timedelta
import jwt


def check_admin(func):
    @wraps(func)
    def wrapped(self, request, *args, **kwargs):
        
        if request.session.get('user_type') != 'admin':
            return redirect('http-403-view')

        return func(self, request, *args, **kwargs)
    return wrapped
