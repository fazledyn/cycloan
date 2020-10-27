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
        owner_pass = request.POST.get('owner-password')

        cursor = connection.cursor()
        sql = "SELECT PASSWORD FROM OWNER WHERE EMAIL_ADDRESS=%s"
        cursor.execute(sql, [owner_email])
        result = cursor.fetchall()
        cursor.close()
        try:
            res = result[0]
            if res == owner_pass:
                print('kaaj hoise')
            else:
                return redirect('login-view')
        except:
            return redirect('login-view')
        # res = result[0]

        # MILLE KI KORA LAGBE ADD KORISH
        
       # return redirect('login-view')


class OwnerSignup(View):
    def get(self, request):
        return redirect('owner-signup')


class CustomerLoginView(View):
    def get(self, request):
        return redirect('login-view')
    
    def post(self, request):
        customer_email  = request.POST.get('customer-email')
        customer_pass   = request.POST.get('customer-password')

        # query db to get things

        cursor = connection.cursor()
        sql = "SELECT PASSWORD FROM CUSTOMER WHERE EMAIL_ADDRESS=%s"
        cursor.execute(sql, [customer_email])
        result = cursor.fetchall()
        cursor.close()
        try:
            res = result[0]
            if res == customer_pass:
                print('kaaj hoise')
            else:
                return redirect('login-view')
        except:
            return redirect('login-view')

