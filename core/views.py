from django.shortcuts import render, redirect
from django.db import connection
from django.views import View


## We will use class based view
## because it is easy to see and understand
## has two member function: GET and POST 


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')


class OwnerLoginView(View):
    def get(self, request):
        return redirect('login-view')

    def post(self, request):
        owner_email = request.POST.get('owner-email')
        owner_pass  = request.POST.get('owner-password')
        
        # query db te get things
        pass


class CustomerLoginView(View):
    def get(self, request):
        return redirect('login-view')
    
    def post(self, request):
        customer_email  = request.POST.get('customer-email')
        customer_pass   = request.POST.get('customer-pass')

        # query db to get things
        pass

