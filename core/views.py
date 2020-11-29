from django.shortcuts import render, redirect
from django.views import View
from django.db import connection

"""
If the user type is owner, it means owner is already logged in. So, redirect to owner dashboard.
Same for customer.
If there is no such value, then they must have logged out. Then send them to login page.
"""


class LoginView(View):
    def get(self, request):
        user_type = request.session.get('user_type')

        if user_type == 'owner':
            return redirect('owner-dashboard-view')
        elif user_type == 'customer':
            return redirect('customer-dashboard-view')
        else:
            return render(request, 'index.html')


