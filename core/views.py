from django.shortcuts import render, redirect
from django.views import View
from django.db import connection
from django.contrib import messages
from django.http import HttpResponseForbidden

from datetime import datetime

from cycloan.settings import SECRET_KEY

import jwt


class IndexView(View):
    def get(self, request):
        user_type = request.session.get('user_type')

        if user_type == 'owner':
            return redirect('owner-dashboard-view')
        elif user_type == 'customer':
            return redirect('customer-dashboard-view')
        else:
            return render(request, 'core/index.html')


class EmailVerificationView(View):

    def get(self, request, verification_token):

        try:
            json = jwt.decode(verification_token, SECRET_KEY, algorithms=['HS256'])

            user_type = json['user_type']
            user_email = json['user_email']
            token_expiry = datetime.fromisoformat(json['token_expiry'])

            if user_type == 'owner':
                # Owner Table Verification
                sql = "SELECT COUNT(*) FROM OWNER_EMAIL_VERIFICATION WHERE TOKEN_VALUE = %s"
                cursor = connection.cursor()
                cursor.execute(sql, [verification_token])
                result = cursor.fetchall()
                cursor.close()

                user_count = int(result[0][0])

                if user_count == 0:
                    messages.warning(request, 'No such accounts exists for verification. Make sure you have completed registration.')
           
                else:
                    sql = "SELECT * FROM OWNER_EMAIL_VERIFICATION WHERE TOKEN_VALUE = %s"
                    cursor = connection.cursor()
                    cursor.execute(sql, [verification_token])
                    result = cursor.fetchall()

                    if result[0][1] == 1:
                        messages.info(request, 'You are already verified')
                    
                    else:
                        if datetime.now() < result[0][5]:
                            sql = "UPDATE OWNER_EMAIL_VERIFICATION SET IS_VERIFIED = %s WHERE TOKEN_VALUE = %s"
                            cursor = connection.cursor()
                            cursor.execute(sql, [1, verification_token])
                            cursor.close()
                            messages.success(request, 'Hoorah ! Your account has been verified. Now you can log in.')
                        
                        else:
                            print("Token Expired")
                            messages.error(request, "Sorry. The token is expired.")

                return redirect('owner-landing-view')

            elif user_type == 'customer':

                sql = "SELECT COUNT(*) FROM CUSTOMER_EMAIL_VERIFICATION WHERE TOKEN_VALUE = %s"
                cursor = connection.cursor()
                cursor.execute(sql, [verification_token])
                result = cursor.fetchall()
                cursor.close()

                user_count = int(result[0][0])

                if user_count == 0:
                    messages.warning(request, 'No such accounts exists for verification. Make sure you have completed registration.')

                else:
                    sql = "SELECT * FROM CUSTOMER_EMAIL_VERIFICATION WHERE TOKEN_VALUE = %s"
                    cursor = connection.cursor()
                    cursor.execute(sql, [verification_token])
                    result = cursor.fetchall()

                    if result[0][1] == 1:
                        messages.info(request, 'You are already verified')

                    else:
                        if datetime.now() < result[0][5]:
                            sql = "UPDATE CUSTOMER_EMAIL_VERIFICATION SET IS_VERIFIED = %s WHERE TOKEN_VALUE = %s"
                            cursor = connection.cursor()
                            cursor.execute(sql, [1, verification_token])
                            cursor.close()
                            messages.success(request, 'Hoorah ! Your account has been verified. Now you can log in.')
                        
                        else:
                            messages.error(request, "Sorry. The token is expired.")
                        
                return redirect('customer-landing-view')

        except:
            messages.error(request, 'Invalid verification token')
            return redirect('http-404-view')



class TripFeedbackView(View):

    def get(self, request, trip_id):
        customer_id = request.session.get('customer_id')

        cursor = connection.cursor()
        sql = "SELECT * FROM TRIP_DETAILS WHERE TRIP_ID = %s"
        cursor.execute(sql, [trip_id])
        result = cursor.fetchall()
        connection.commit()
        cursor.close()

        context = {
            'trip_id': trip_id,
            'trip': result[0]
        }

        return render(request, 'core/trip_feedback.html', context)


    def post(self, request, trip_id):
        customer_id = request.session.get('customer_id')

        print(" ======================================== ")
        print(request.POST)

        cycle_rating = request.POST.get('cycle_rating')
        cycle_comment = request.POST.get('cycle_comment')
        owner_rating = request.POST.get('owner_rating')
        owner_comment = request.POST.get('owner_comment')

        cursor = connection.cursor()
        cursor.callproc("REVIEW_INSERT", [cycle_rating, cycle_comment, owner_rating, owner_comment, trip_id])
        cursor.close()

        messages.success(request, 'Your review has been added')
        return redirect('customer-dashboard-view')



class Http403View(View):
    def get(self, request):
        return render(request, 'core/403.html')


class Http404View(View):
    def get(self, request):
        return render(request, 'core/404.html')
