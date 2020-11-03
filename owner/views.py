from typing import Dict, Any

from django.db import connection
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View

from .utils import save_owner_photo
from core.utils import create_auth_token

## decorators
from core.utils import verify_auth_token, check_owner


class OwnerLoginView(View):

    def get(self, request):
        if request.session.get('auth_token'):
            return redirect('owner-dashboard-view')
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
            fetched_pass = result[0][0]
            if fetched_pass == owner_pass:
                owner_id = result[0][1]

                request.session['owner_id'] = owner_id
                request.session['auth_token'] = create_auth_token(owner_id)
                request.session['user_type'] = 'owner'
                return redirect('owner-dashboard-view')

            else:
                messages.error(request, 'Password did not match. Enter correctly!')
                return redirect('login-view')
        except:
            messages.error(request, 'Your email address is not found in our database. Enter it correctly!')
            return redirect('login-view')


class OwnerRegisterView(View):
    def get(self, request):
        if request.session.get('auth_token'):
            return redirect('owner-dashboard-view')
        return render(request, 'owner_register.html')

    def post(self, request):

        photo = request.FILES.get('photo')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        fullname = request.POST.get('fullname')
        contact = request.POST.get('contact')
        location = request.POST.get('location')

        if password != password_confirm:
            messages.warning(request, 'Passwords do not match. Check again')
            return redirect('owner-register-view')
        else:
            cursor = connection.cursor()
            sql = "SELECT COUNT(*) FROM OWNER WHERE EMAIL_ADDRESS=%s"
            cursor.execute(sql, [email])
            result = cursor.fetchall()
            cursor.close()
            count = int(result[0][0])

            if count == 0:
                cursor = connection.cursor()
                sql = "SELECT COUNT(*) FROM OWNER"
                cursor.execute(sql)
                result = cursor.fetchall()
                cursor.close()
                count = int(result[0][0])
                owner_id = 101 + count
                photo_path = save_owner_photo(photo, owner_id)

                cursor = connection.cursor()
                sql = "INSERT INTO OWNER(OWNER_ID,OWNER_NAME,PASSWORD,OWNER_PHONE,LOCATION,PHOTO,EMAIL_ADDRESS) VALUES(%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, [owner_id, fullname, password, contact, location, photo_path, email])
                connection.commit()
                cursor.close()

                cursor = connection.cursor()
                sql = "INSERT INTO OWNER_EMAIL_VERIFICATION(OWNER_ID,IS_VERIFIED,EMAIL_ADDRESS) VALUES(%s, %s, %s)"
                cursor.execute(sql, [owner_id, 0, email])
                connection.commit()
                cursor.close()

                messages.success(request, 'Account create successful. Now you can login.')
                return redirect('login-view')
                
            else:
                messages.warning(request, 'Account exists with similar email. Please provide different email')
                return redirect('owner-register-view')


class OwnerDashboardView(View):

    @verify_auth_token
    @check_owner
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
