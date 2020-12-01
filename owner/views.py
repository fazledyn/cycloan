from typing import Dict, Any

from django.db import connection
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View

from .utils import save_owner_photo
from core.utils import create_auth_token, send_verification_email

from datetime import datetime, timedelta
import jwt, threading

from cycloan.settings import SECRET_KEY

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

                cursor = connection.cursor()
                sql = "SELECT IS_VERIFIED FROM OWNER_EMAIL_VERIFICATION WHERE EMAIL_ADDRESS=%s"
                cursor.execute(sql, [owner_email])
                verify = cursor.fetchall()
                cursor.close()
                v = int(verify[0][0])

                if v == 0:
                    messages.error(request, 'Email has not been verified yet. Please check your email and verify.')
                    return redirect('login-view')
                else:
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
        # InMemoryUplaodedFile
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
                owner_count = 10001 + count
                photo_path = save_owner_photo(photo, owner_count, contact)

                cursor = connection.cursor()
                sql = "INSERT INTO OWNER(OWNER_ID,OWNER_NAME,PASSWORD,OWNER_PHONE,LOCATION,PHOTO_PATH,EMAIL_ADDRESS) VALUES(OWNER_INCREMENT.NEXTVAL, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, [fullname, password, contact, location, photo_path, email])
                connection.commit()
                cursor.close()

                cursor = connection.cursor()
                sql = "SELECT OWNER_ID FROM OWNER WHERE EMAIL_ADDRESS=%s"
                cursor.execute(sql, [email])
                result = cursor.fetchall()
                cursor.close()
                owner_id = result[0][0]

                """
                TOKEN MAKING
                """
                token_created = datetime.now()
                token_expiry = token_created + timedelta(days=1)

                verification_token = jwt.encode(
                    {
                        'user_type': 'owner',
                        'user_id': owner_id,
                        'token_expiry': str(token_expiry)
                    }, SECRET_KEY, algorithm='HS256'
                ).decode('utf-8')

                cursor = connection.cursor()
                sql = "INSERT INTO OWNER_EMAIL_VERIFICATION(OWNER_ID, IS_VERIFIED, EMAIL_ADDRESS, TOKEN_CREATED, TOKEN_EXPIRY, TOKEN_VALUE) VALUES(%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, [owner_id, 0, email, token_created, token_expiry, verification_token])
                connection.commit()
                cursor.close()

                print("#################################################")
                print("VER TOKEN: ", verification_token)
                print("#################################################")

                email_thread = threading.Thread(target=send_verification_email,
                                                args=(email, fullname, 'owner', verification_token))
                email_thread.start()

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
        sql = "SELECT OWNER_NAME FROM OWNER WHERE OWNER_ID = %s"
        cursor.execute(sql, [ owner_id ])
        owner_name = cursor.fetchall()

        cursor = connection.cursor()
        sql = "SELECT CYCLE_ID, MODEL, STATUS, RATING FROM CYCLE WHERE OWNER_ID = %s"
        cursor.execute(sql, [ owner_id ])
        cycle_list = cursor.fetchall()

        context = {
            'owner_name': owner_name[0][0],
            'cycle_list': cycle_list
        }
        return render(request, 'owner_dashboard.html', context)

    def post(self, request):
        owner_id = request.session.get('owner_id')
        model = request.POST.get('model')
        photo = request.FILES.get('photo')

        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM CYCLE WHERE OWNER_ID = %s"
        cursor.execute(sql, [owner_id])
        result = cursor.fetchall()
        cursor.close()

        count_cycle = int(result[0][0])
        count_cycle = count_cycle + 1

        ## NEED TO PASS THE NUMBER OF CYCLE AN OWNER HAS AND THE OWNER_ID NUMBER TO THE PHOTO_PATH FUNCTION
        photo_path = save_owner_photo(photo, count_cycle, owner_id)

        cursor = connection.cursor()
        sql = "INSERT INTO CYCLE(CYCLE_ID,MODEL,STATUS,PHOTO_PATH,OWNER_ID) VALUES(CYCLE_INCREMENT.NEXTVAL, %s, %s, %s, %s)"
        cursor.execute(sql, [model, 0, photo_path, owner_id])
        connection.commit()
        cursor.close()


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
                cursor = connection.cursor()
                sql = "SELECT OWNER_PHONE FROM OWNER WHERE OWNER_ID = %s"
                cursor.execute(sql, [owner_id])
                result = cursor.fetchall()
                cursor.close()
                contact = result[0][0]

                new_photo_path = save_owner_photo(owner_new_photo, owner_id, contact)
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
