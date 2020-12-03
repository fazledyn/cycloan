from django.db import connection
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from core.utils import create_auth_token


class AdminLoginView(View):
    def get(self, request):
        print('hello')
        return redirect('login-view-for-admin')

    def post(self, request):
        admin_email = request.POST.get('admin-email')
        admin_pass = request.POST.get('admin-password')

        cursor = connection.cursor()
        sql = "SELECT ADMIN_PASSWORD, ADMIN_ID FROM ADMIN WHERE ADMIN_EMAIL=%s"
        cursor.execute(sql, [admin_email])
        result = cursor.fetchall()
        cursor.close()

        try:
            fetched_pass = result[0][0]
            if fetched_pass == admin_pass:
                admin_id = result[0][1]
                request.session['admin_id'] = admin_id
                request.session['auth_token'] = create_auth_token(admin_id)
                request.session['user_type'] = 'admin'
                return redirect('admin-dashboard-view')

            else:
                messages.error(request, 'Password did not match. Enter correctly!')
                return redirect('admin-login-view')
        except:
            messages.error(request, 'Your email address is not found in our database. Enter it correctly!')
            return redirect('admin-login-view')


class AdminDashboardView(View):

    # @verify_auth_token
    # @check_customer
    def get(self, request):
        admin_id = request.session.get('admin_id')

        cursor = connection.cursor()
        sql = "SELECT ADMIN_NAME FROM ADMIN WHERE ADMIN_ID=%s"
        cursor.execute(sql, [admin_id])
        result = cursor.fetchall()
        cursor.close()

        admin_name = result[0][0]
        context = {'admin_name': admin_name}

        return render(request, 'admin_dashboard.html', context)
