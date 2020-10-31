from django.shortcuts import render, redirect
from django.db import connection
from django.views import View
from django.contrib import messages


class CustomerLoginView(View):

    def get(self, request):
        return redirect('login-view')

    def post(self, request):
        customer_email = request.POST.get('customer-email')
        customer_pass = request.POST.get('customer-password')

        cursor = connection.cursor()
        sql = "SELECT PASSWORD, CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ADDRESS=%s"
        cursor.execute(sql, [customer_email])
        result = cursor.fetchall()
        cursor.close()

        try:
            res = result[0][0]
            if res == customer_pass:
                print('kaaj hoise')
                request.session['customer_id'] = result[0][1]
                print(request.session['customer_id'])
                return redirect('customer-dashboard-view')
            else:
                messages.error(request, 'Password mismatched. Enter correctly!')
                return redirect('login-view')

        except:
            messages.error(request, 'Your email was not found in database. Enter correctly!')
            return redirect('login-view')


class CustomerRegisterView(View):

    def get(self, request):
        return render(request, 'customer_register.html')

    def post(self, request):
        # eitar kaaj kora lagbe
        pass


class CustomerDashboardView(View):

    def get(self, request):
        customer_id = request.session['customer_id']
        cursor = connection.cursor()
        sql = "SELECT CUSTOMER_NAME FROM CUSTOMER WHERE CUSTOMER_ID=%s"
        cursor.execute(sql, [customer_id])
        result = cursor.fetchall()
        cursor.close()
        customer_name = result[0][0]
        print(customer_name)
        context = {'customer_name': customer_name}
        return render(request, 'customer_dashboard.html', context)
