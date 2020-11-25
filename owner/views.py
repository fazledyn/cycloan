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


class OwnerLogoutView(View):
    
    @verify_auth_token
    @check_owner
    def get(self, request):
        request.session.pop('owner_id', None)    
        request.session.pop('user_type', None)
        request.session.pop('auth_token', None)
        messages.info(request, 'You are logged out.')
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
                sql = "INSERT INTO OWNER(OWNER_ID,OWNER_NAME,PASSWORD,OWNER_PHONE,LOCATION,PHOTO_PATH,EMAIL_ADDRESS) VALUES(%s, %s, %s, %s, %s, %s, %s)"
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


class OwnerProfileView(View):

    @verify_auth_token
    @check_owner
    def get(self, request):
        cursor = connection.cursor()

        owner_id = request.session.get('owner_id')
        sql = "SELECT * FROM OWNER WHERE OWNER_ID=%s"
        cursor.execute(sql, [owner_id])
        result = cursor.fetchall()
        cursor.close()

        owner_id = result[0][0]
        owner_name = result[0][1]
        owner_photo = result[0][3]
        owner_phone = result[0][4]
        owner_email = result[0][5]

        context = {
            'owner_id': owner_id,
            'owner_name': owner_name,
            'owner_photo': owner_photo,
            'owner_phone': owner_phone,
            'owner_email': owner_email
        }

        return render(request, 'owner_profile.html', context)

    @verify_auth_token
    @check_owner
    def post(self, request):

        cursor = connection.cursor()
        owner_id = request.session.get('owner_id')
        sql = "SELECT PASSWORD FROM OWNER WHERE OWNER_ID = %s"
        cursor.execute(sql, [owner_id])
        result = cursor.fetchall()
        cursor.close()        

        #####################   WORK LEFT   ####################
        ########################################################

        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password_confirm = request.POST.get('new_password_confirm')

        owner_new_phone = request.POST.get('owner_new_phone')
        owner_new_photo = request.FILES.get('owner_new_photo')

        old_password_from_db = result[0][0]

        if old_password == "" and new_password == "" and new_password_confirm == "":
            
            if len(request.FILES) != 0:
                new_photo_path = save_owner_photo(owner_new_photo, owner_id)
                cursor = connection.cursor()
                sql = "UPDATE OWNER SET PHOTO_PATH = %s WHERE OWNER_ID = %s"
                cursor.execute(sql, [new_photo_path, owner_id])
                connection.commit()
                cursor.close()
            
            cursor = connection.cursor()
            sql = "UPDATE OWNER SET OWNER_PHONE = %s WHERE OWNER_ID = %s"
            cursor.execute(sql, [owner_new_phone, owner_id])
            connection.commit()
            cursor.close()
            
            messages.success(request, 'Profile updated !')

        else:
            if new_password == new_password_confirm:
                
                if old_password == old_password_from_db:        
                    cursor = connection.cursor()
                    sql = "UPDATE OWNER SET PASSWORD = %s WHERE OWNER_ID = %s"
                    cursor.execute(sql, [new_password, owner_id])
                    connection.commit()
                    cursor.close()
                    messages.success(request, 'Password updated !')
            
                else:
                    messages.error('Enter current password correctly!')

            else:
                messages.error('The new passwords do not match! Type carefully.')
    
        return redirect('owner-profile-view')
