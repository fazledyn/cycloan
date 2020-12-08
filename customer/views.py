
import hashlib
from django.shortcuts import render, redirect
from django.db import connection
from django.views import View
from django.contrib import messages

from .utils import save_customer_doc, save_customer_photo, calculate_distance
from core.utils import create_auth_token, send_verification_email, create_verification_token
from cycloan.settings import SECRET_KEY
from cycloan.settings import TRIP_COMPLETED, TRIP_ONGOING, TRIP_REJECTED, TRIP_REQUESTED, TRIP_REVIEWED
from cycloan.settings import CYCLE_AVAILABLE, CYCLE_BOOKED
from cycloan.settings import DLAT, DLONG

from datetime import datetime, timedelta
import jwt
import threading

# decorators
from core.utils import verify_auth_token, check_customer


class CustomerLandingView(View):
    def get(self, request):
        if request.session.get('auth_token'):
            return redirect('customer-dashboard-view')
        return render(request, 'customer_landing.html')


class CustomerLoginView(View):

    def post(self, request):
        customer_email = request.POST.get('customer-email')
        customer_pass = request.POST.get('customer-password')

        cursor = connection.cursor()
        sql = "SELECT PASSWORD, CUSTOMER_ID, PHOTO_PATH, CUSTOMER_NAME FROM CUSTOMER WHERE EMAIL_ADDRESS=%s"
        cursor.execute(sql, [customer_email])
        result = cursor.fetchall()
        cursor.close()

        try:
            fetched_pass = result[0][0]
            hashed_customer_password = hashlib.sha256(
                customer_pass.encode()).hexdigest()

            if fetched_pass == hashed_customer_password:
                customer_id = result[0][1]
                customer_photo = result[0][2]
                customer_name = result[0][3]

                cursor = connection.cursor()
                sql = "SELECT IS_VERIFIED FROM CUSTOMER_EMAIL_VERIFICATION WHERE EMAIL_ADDRESS=%s"
                cursor.execute(sql, [customer_email])
                verify = cursor.fetchall()
                cursor.close()
                v = int(verify[0][0])

                if v == 0:
                    messages.error(
                        request, 'Email has not been verified yet. Please check your email and verify.')
                    return redirect('customer-landing-view')
                else:
                    request.session['customer_id'] = customer_id
                    request.session['auth_token'] = create_auth_token(
                        customer_id)
                    request.session['user_type'] = 'customer'
                    request.session['user_name'] = customer_name
                    request.session['user_photo'] = customer_photo
                    request.session['user_email'] = customer_email
                    return redirect('customer-dashboard-view')
            else:
                messages.error(
                    request, 'Password mismatched. Enter correctly!')
                return redirect('customer-landing-view')
        except:
            messages.error(
                request, 'Your email was not found in database. Enter correctly!')
            return redirect('customer-landing-view')


class CustomerLogoutView(View):
    @verify_auth_token
    @check_customer
    def get(self, request):
        request.session.pop('customer_id', None)
        request.session.pop('user_type', None)
        request.session.pop('auth_token', None)
        request.session.pop('user_photo', None)
        request.session.pop('user_name', None)
        request.session.pop('user_email', None)

        messages.info(request, 'You are logged out.')
        return redirect('customer-landing-view')


class CustomerRegisterView(View):

    def post(self, request):

        photo = request.FILES.get('photo')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        fullname = request.POST.get('fullname')
        contact = request.POST.get('contact')
        doctype = request.POST.get('doctype')
        document = request.FILES.get('document')

        if password != password_confirm:
            messages.warning(request, 'Passwords do not match. Check again')
            return redirect('customer-landing-view')

        else:
            cursor = connection.cursor()
            sql = "SELECT COUNT(*) FROM CUSTOMER WHERE EMAIL_ADDRESS=%s"
            cursor.execute(sql, [email])
            result = cursor.fetchall()
            cursor.close()
            count = int(result[0][0])

            if count == 0:
                cursor = connection.cursor()
                sql = "SELECT COUNT(*) FROM CUSTOMER"
                cursor.execute(sql)
                result = cursor.fetchall()
                cursor.close()

                count = int(result[0][0])
                customer_count = 50001 + count
                photo_path = save_customer_photo(
                    photo, customer_count, contact)
                doc_path = save_customer_doc(document, customer_count, contact)

                token_created = datetime.now()
                token_expiry = token_created + timedelta(days=1)
                verification_token = create_verification_token(
                    "customer", email, token_expiry)

                hashed_password = hashlib.sha256(password.encode()).hexdigest()

                cursor = connection.cursor()
                cursor.callproc("INSERT_CUSTOMER",
                                [fullname, email, hashed_password, contact, photo_path, doc_path, doctype, token_created,
                                 token_expiry, verification_token])
                cursor.close()

                email_thread = threading.Thread(target=send_verification_email,
                                                args=(email, fullname, 'customer', verification_token))
                email_thread.start()

                messages.success(request,
                                 'Successfully created account. Now you must verify your email and then you can log in.')
                return redirect('customer-landing-view')

            else:
                messages.warning(
                    request, 'Account exists with similar email. Please provide different email')
                return redirect('customer-landing-view')


class CustomerDashboardView(View):

    @verify_auth_token
    @check_customer
    def get(self, request):
        customer_id = request.session.get('customer_id')

        # This section is for ongoing trips where the owner has given approval to use their cycle.
        cursor = connection.cursor()
        sql = """
                SELECT TD.TRIP_ID, TD.START_DATE_TIME, TD.END_DATE_TIME, O.OWNER_ID, O.OWNER_NAME, C.PHOTO_PATH, FARE_CALCULATION(TD.TRIP_ID)
                FROM TRIP_DETAILS TD, CYCLE C, OWNER O
                WHERE TD.CYCLE_ID = C.CYCLE_ID
                AND TD.CUSTOMER_ID = %s
                AND TD.STATUS = %s
            """
        cursor.execute(sql, [customer_id, TRIP_ONGOING])
        ongoing_trip = cursor.fetchall()
        connection.commit()
        cursor.close()

        # The part for cycle request put
        cursor = connection.cursor()
        sql = """
                SELECT TD.TRIP_ID, C.PHOTO_PATH, TD.START_DATE_TIME, TD.END_DATE_TIME, C.FARE_PER_DAY, C.MODEL, C.CYCLE_ID
                FROM TRIP_DETAILS TD, CYCLE C
                WHERE TD.CYCLE_ID = C.CYCLE_ID
                AND TD.CUSTOMER_ID = %s
                AND TD.STATUS = %s
            """
        cursor.execute(sql, [customer_id, TRIP_REQUESTED])
        requested_cycle_list = cursor.fetchall()
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        sql = """
                SELECT *
                FROM TRIP_DETAILS TD, CYCLE C
                WHERE TD.CYCLE_ID = C.CYCLE_ID
                AND TD.CUSTOMER_ID = %s
                AND TD.STATUS = %s
                """
        cursor.execute(sql, [customer_id, TRIP_COMPLETED])
        completed_trip = cursor.fetchall()
        connection.commit()
        cursor.close()

        context = {
            'ongoing_trip': ongoing_trip,
            'requested_cycle_list': requested_cycle_list,
            'completed_trip': completed_trip,
        }

        return render(request, 'customer_dashboard.html', context)

    @verify_auth_token
    @check_customer
    def post(self, request):

        customer_lat = request.POST.get('latitude')
        customer_long = request.POST.get('longtitude')
        preference = request.POST.get('preference')

        customer_lat = float(customer_lat)
        customer_long = float(customer_long)

        customer_id = request.session.get('customer_id')
        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM TRIP_DETAILS WHERE (STATUS=%s OR STATUS=%s) AND CUSTOMER_ID=%s"
        cursor.execute(sql, [TRIP_ONGOING, TRIP_REQUESTED, customer_id])
        result = cursor.fetchall()
        count = int(result[0][0])

        if count == 0:
            cursor = connection.cursor()

            if preference == "1":
                sql = """
                        SELECT C.CYCLE_ID, O.LATITUDE, O.LONGTITUDE, O.OWNER_NAME, O.OWNER_ID, C.FARE_PER_DAY, O.OWNER_PHONE, C.PHOTO_PATH
                        FROM CYCLE C, OWNER O
                        WHERE C.OWNER_ID = O.OWNER_ID
                        AND ABS(O.LATITUDE - %s) <= %s
                        AND ABS(O.LONGTITUDE - %s) <= %s
                        AND C.STATUS = %s
                    """
                cursor.execute(sql, [customer_lat, DLAT, customer_long, DLONG, 0])

            else:
                sql = """
                        SELECT C.CYCLE_ID, O.LATITUDE, O.LONGTITUDE, O.OWNER_NAME, O.OWNER_ID, C.FARE_PER_DAY, O.OWNER_PHONE, C.PHOTO_PATH
                        FROM CYCLE C, OWNER O
                        WHERE C.OWNER_ID = O.OWNER_ID
                        AND C.STATUS = %s
                    """
                cursor.execute(sql, [CYCLE_AVAILABLE])
            
            result = cursor.fetchall()

            if len(result) == 0:
                print("There are no cycles to show")
                messages.info(request, "There are no cycles to show")
                context = {}

            else:
                print("There are cycles to show")

                list_length = len(result)
                for i in range(list_length):
                    dist = calculate_distance(baseLat=customer_lat, baseLong=customer_long, pointLat=result[i][1], pointLong=result[i][2])
                    dist = round(dist, 2)
                    result[i] += (dist,)

                context = { 'cycle_list': result}

            return render(request, 'customer_dashboard.html', context)

        else:
            messages.info(
                request, "You are not allowed to find cycle while a trip is ongoing or a request is being processed.")
            return redirect('customer-dashboard-view')


class CustomerProfileView(View):

    @verify_auth_token
    @check_customer
    def get(self, request):
        print(request.session['auth_token'])

        cursor = connection.cursor()

        customer_id = request.session.get('customer_id')
        sql = "SELECT * FROM CUSTOMER WHERE CUSTOMER_ID=%s"
        cursor.execute(sql, [customer_id])
        result = cursor.fetchall()
        cursor.close()

        customer_id = result[0][0]
        customer_name = result[0][1]
        customer_photo = result[0][3]
        customer_phone = result[0][4]
        customer_email = result[0][5]

        context = {
            'customer_id': customer_id,
            'customer_name': customer_name,
            'customer_photo': customer_photo,
            'customer_phone': customer_phone,
            'customer_email': customer_email
        }

        return render(request, 'customer_profile.html', context)

    @verify_auth_token
    @check_customer
    def post(self, request):

        cursor = connection.cursor()
        customer_id = request.session.get('customer_id')
        sql = "SELECT PASSWORD FROM CUSTOMER WHERE CUSTOMER_ID=%s"
        cursor.execute(sql, [customer_id])
        result = cursor.fetchall()
        cursor.close()

        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password_confirm = request.POST.get('new_password_confirm')

        customer_new_phone = request.POST.get('customer_new_phone')
        customer_new_photo = request.FILES.get('customer_new_photo')

        old_password_from_db = result[0][0]

        if old_password == "" and new_password == "" and new_password_confirm == "":

            if len(request.FILES) != 0:
                cursor = connection.cursor()
                sql = "SELECT CUSTOMER_PHONE FROM CUSTOMER WHERE CUSTOMER_ID = %s"
                cursor.execute(sql, [customer_id])
                result = cursor.fetchall()
                cursor.close()

                contact = result[0][0]
                new_photo_path = save_customer_photo(
                    customer_new_photo, customer_id, contact)
                cursor = connection.cursor()
                sql = "UPDATE CUSTOMER SET PHOTO_PATH = %s WHERE CUSTOMER_ID = %s"
                cursor.execute(sql, [new_photo_path, customer_id])
                connection.commit()
                cursor.close()

                request.session['user_photo'] = new_photo_path

            cursor = connection.cursor()
            sql = "UPDATE CUSTOMER SET CUSTOMER_PHONE = %s WHERE CUSTOMER_ID = %s"
            cursor.execute(sql, [customer_new_phone, customer_id])
            connection.commit()
            cursor.close()

            messages.success(request, 'Profile updated !')

        else:
            print("THATTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
            if new_password == new_password_confirm:
                hashed_old_password = hashlib.sha256(
                    old_password.encode()).hexdigest()
                hashed_new_password = hashlib.sha256(
                    new_password.encode()).hexdigest()

                if hashed_old_password == old_password_from_db:
                    cursor = connection.cursor()
                    sql = "UPDATE CUSTOMER SET PASSWORD = %s WHERE CUSTOMER_ID = %s"
                    cursor.execute(sql, [hashed_new_password, customer_id])
                    connection.commit()
                    cursor.close()
                    messages.success(request, 'Password updated !')
                else:
                    messages.error('Enter current password correctly!')
            else:
                messages.error(
                    'The new passwords do not match! Type carefully.')

        return redirect('customer-profile-view')


class CustomerTripHistoryView(View):

    def get(self, request):
        customer_id = request.session.get('customer_id')

        cursor = connection.cursor()
        sql = """
                    SELECT TD.TRIP_ID, TD.STATUS, O.OWNER_ID, C.CYCLE_ID, FARE_CALCULATION(TD.TRIP_ID), TD.START_DATE_TIME, TD.END_DATE_TIME
                    FROM TRIP_DETAILS TD, OWNER O, CYCLE C
                    WHERE TD.CYCLE_ID = C.CYCLE_ID
                    AND C.OWNER_ID = O.OWNER_ID
                    AND TD.CUSTOMER_ID = %s
                    AND (TD.STATUS = %s OR TD.STATUS = %s OR TD.STATUS = %s)
                """
        cursor.execute(sql, [customer_id, TRIP_COMPLETED,
                             TRIP_REJECTED, TRIP_REVIEWED])
        trips = cursor.fetchall()
        connection.commit()
        cursor.close()

        context = {'trip_list': trips}
        return render(request, 'customer_trip_history.html', context)
