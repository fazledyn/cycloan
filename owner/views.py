import hashlib
from typing import Dict, Any

from django.db import connection
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View

from .utils import save_owner_photo
from core.utils import create_auth_token, send_verification_email, create_verification_token

from datetime import datetime, timedelta
import jwt, threading

from cycloan.settings import SECRET_KEY
from cycloan.settings import CYCLE_BOOKED, CYCLE_AVAILABLE
from cycloan.settings import TRIP_REQUESTED, TRIP_ONGOING, TRIP_REJECTED, TRIP_COMPLETED, TRIP_REVIEWED

## decorators
from core.utils import verify_auth_token, check_owner


class OwnerLandingView(View):
    def get(self, request):
        if request.session.get('auth_token'):
            return redirect('owner-dashboard-view')
        return render(request, 'owner_landing.html')


class OwnerLoginView(View):

    def post(self, request):
        owner_email = request.POST.get('owner-email')
        owner_pass = request.POST.get('owner-password')

        cursor = connection.cursor()
        sql = "SELECT PASSWORD, OWNER_ID, PHOTO_PATH, OWNER_NAME FROM OWNER WHERE EMAIL_ADDRESS=%s"
        cursor.execute(sql, [owner_email])
        result = cursor.fetchall()
        cursor.close()

        try:
            fetched_pass = result[0][0]
            hashed_owner_password = hashlib.sha256(owner_pass.encode()).hexdigest()
            
            if fetched_pass == hashed_owner_password:
                owner_id = result[0][1]
                owner_photo = result[0][2]
                owner_name = result[0][3]

                cursor = connection.cursor()
                sql = "SELECT IS_VERIFIED FROM OWNER_EMAIL_VERIFICATION WHERE EMAIL_ADDRESS=%s"
                cursor.execute(sql, [owner_email])
                verify = cursor.fetchall()
                cursor.close()
                v = int(verify[0][0])

                if v == 0:
                    messages.error(request, 'Email has not been verified yet. Please check your email and verify.')
                    return redirect('owner-landing-view')
                else:
                    request.session['owner_id'] = owner_id
                    request.session['auth_token'] = create_auth_token(owner_id)
                    request.session['user_type'] = 'owner'
                    request.session['user_name'] = owner_name
                    request.session['user_email'] = owner_email
                    request.session['user_photo'] = owner_photo
                    return redirect('owner-dashboard-view')

            else:
                messages.error(request, 'Password did not match. Enter correctly!')
                return redirect('owner-landing-view')
        except:
            messages.error(request, 'Your email address is not found in our database. Enter it correctly!')
            return redirect('owner-landing-view')


class OwnerLogoutView(View):

    @verify_auth_token
    @check_owner
    def get(self, request):
        request.session.pop('owner_id', None)
        request.session.pop('user_type', None)
        request.session.pop('auth_token', None)
        request.session.pop('user_email', None)
        request.session.pop('user_photo', None)
        request.session.pop('user_name', None)
        
        messages.info(request, "You are logged out.")
        return redirect('owner-landing-view')


class OwnerRegisterView(View):

    def post(self, request):

        photo = request.FILES.get('photo')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        fullname = request.POST.get('fullname')
        contact = request.POST.get('contact')
        
        longtitude = request.POST.get('longtitude')
        latitude = request.POST.get('latitude')

        longtitude = float(longtitude)
        latitude = float(latitude)

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

                token_created = datetime.now()
                token_expiry = token_created + timedelta(days=1)
                verification_token = create_verification_token("owner", email, token_expiry)

                hashed_password = hashlib.sha256(password.encode()).hexdigest()

                cursor = connection.cursor()
                cursor.callproc("INSERT_OWNER", [fullname, email, hashed_password, contact, photo_path, longtitude, latitude, token_created, token_expiry, verification_token])
                cursor.close()

                email_thread = threading.Thread(target=send_verification_email,
                                                args=(email, fullname, 'owner', verification_token))
                email_thread.start()

                messages.success(request, 'Successfully created account. Now you must verify your email and then you can log in.')
                return redirect('owner-landing-view')

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
        connection.commit()
        cursor.close()
        
        cursor = connection.cursor()
        sql =   """
                SELECT TD.TRIP_ID, TD.CUSTOMER_ID, CS.CUSTOMER_NAME, C.PHOTO_PATH, TD.START_DATE_TIME, TD.END_DATE_TIME, TD.PAYMENT_TYPE, FARE_CALCULATION(TD.TRIP_ID)
                FROM TRIP_DETAILS TD, CYCLE C, CUSTOMER CS
                WHERE TD.CYCLE_ID = C.CYCLE_ID
                AND CS.CUSTOMER_ID = TD.CUSTOMER_ID
                AND C.OWNER_ID = %s
                AND TD.STATUS = %s
                """
        cursor.execute(sql, [ owner_id, TRIP_REQUESTED ])
        cycle_request_list = cursor.fetchall()
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        sql =   """
                SELECT TD.TRIP_ID, TD.START_DATE_TIME, TD.END_DATE_TIME, CS.CUSTOMER_ID, CS.CUSTOMER_NAME, C.PHOTO_PATH, FARE_CALCULATION(TD.TRIP_ID) 
                FROM TRIP_DETAILS TD, CYCLE C, CUSTOMER CS
                WHERE TD.CYCLE_ID = C.CYCLE_ID
                AND TD.CUSTOMER_ID = CS.CUSTOMER_ID
                AND C.OWNER_ID = %s
                AND TD.STATUS = %s
                """
        cursor.execute(sql, [ owner_id, TRIP_ONGOING ])
        ongoing_trip = cursor.fetchall()
        connection.commit()
        cursor.close()

        context = {
            'owner_name': owner_name[0][0],
            'cycle_request_list': cycle_request_list,
            'ongoing_trip': ongoing_trip
        }
        return render(request, 'owner_dashboard.html', context)


class OwnerCycleView(View):

    def get(self, request):
        owner_id = request.session.get('owner_id')

        cursor = connection.cursor()
        sql = "SELECT * FROM CYCLE WHERE OWNER_ID = %s"
        cursor.execute(sql, [ owner_id ])
        cycle_list = cursor.fetchall()
        connection.commit()
        cursor.close()

        context = { 'cycle_list': cycle_list }
        return render(request, 'owner_cycle.html', context)


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

                request.session['user_photo'] = new_photo_path

            cursor = connection.cursor()
            sql = "UPDATE OWNER SET OWNER_PHONE = %s WHERE OWNER_ID = %s"
            cursor.execute(sql, [owner_new_phone, owner_id])
            connection.commit()
            cursor.close()

            messages.success(request, 'Profile updated !')

        else:
            if new_password == new_password_confirm:
                hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
                hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()

                if hashed_old_password == old_password_from_db:
                    cursor = connection.cursor()
                    sql = "UPDATE OWNER SET PASSWORD = %s WHERE OWNER_ID = %s"
                    cursor.execute(sql, [hashed_new_password, owner_id])
                    connection.commit()
                    cursor.close()
                    messages.success(request, 'Password updated !')
                else:
                    messages.error('Enter current password correctly!')
            else:
                messages.error('The new passwords do not match! Type carefully.')

        return redirect('owner-profile-view')


class OwnerTripHistoryView(View):

    def get(self, request):
        owner_id = request.session.get('owner_id')

        cursor = connection.cursor()
        sql =   """
                    SELECT TD.TRIP_ID, TD.STATUS, CS.CUSTOMER_ID, C.CYCLE_ID, FARE_CALCULATION(TD.TRIP_ID), TD.START_DATE_TIME, TD.END_DATE_TIME, CS.CUSTOMER_NAME
                    FROM TRIP_DETAILS TD, CYCLE C, CUSTOMER CS
                    WHERE TD.CYCLE_ID = C.CYCLE_ID
                    AND CS.CUSTOMER_ID = TD.CUSTOMER_ID
                    AND C.OWNER_ID = %s
                    AND (TD.STATUS = %s OR TD.STATUS = %s)
                """
        cursor.execute(sql, [owner_id, TRIP_COMPLETED, TRIP_REVIEWED])
        trips = cursor.fetchall()
        connection.commit()
        cursor.close()

        context = { 'trip_list': trips }
        return render(request, 'owner_trip_history.html', context)

