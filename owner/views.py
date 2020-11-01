from typing import Dict, Any

from django.db import connection
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View


class OwnerLoginView(View):

    def get(self, request):
        return redirect('login-view')

    def post(self, request):
        owner_email = request.POST.get('owner-email')
        owner_pass = request.POST.get('owner-password')

        cursor = connection.cursor()
        sql = "SELECT PASSWORD, OWNER_ID FROM OWNER WHERE EMAIL_ADDRESS=%s"
        cursor.execute(sql, [owner_email])
        result = cursor.fetchall()
        cursor.close()
        
        try:
            res = result[0][0]
            if res == owner_pass:
                print('kaaj hoise')
                request.session['owner_id'] = result[0][1]
                print(request.session['owner_id'])
                return redirect('owner-dashboard-view')
            else:
                messages.error(request, 'Password did not match. Enter correctly!')
                return redirect('login-view')
        except:
            messages.error(request, 'Your email address is not found in our database. Enter it correctly!')
            return redirect('login-view')


class OwnerRegisterView(View):
    def get(self, request):
        return render(request, 'owner_register.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        fullname = request.POST.get('fullname')
        contact = request.POST.get('contact')
        location = request.POST.get('location')

        if password != password_confirm:
            return redirect('owner-register-view')
        else:
            cursor = connection.cursor()
            sql = "SELECT COUNT(*) FROM OWNER"
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            count = int(result[0][0])

            cursor = connection.cursor()
            sql = "INSERT INTO OWNER(OWNER_ID,OWNER_NAME,PASSWORD,OWNER_PHONE,LOCATION,EMAIL_ADDRESS) VALUES(%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, [101+count, fullname, password, contact, location, email])
            connection.commit()
            cursor.close()
            return redirect('owner-dashboard-view')



class OwnerDashboardView(View):

    def get(self, request):
        owner_id = request.session.get('owner_id')
        cursor = connection.cursor()
        sql = "SELECT OWNER_NAME FROM OWNER WHERE OWNER_ID=%s"
        cursor.execute(sql, [owner_id])
        result = cursor.fetchall()
        cursor.close()
        owner_name = result[0][0]
        context = {'owner_name': owner_name}
        return render(request, 'owner_dashboard.html', context)