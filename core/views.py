from django.shortcuts import render, redirect
from django.views import View
from django.db import connection
from django.contrib import messages

from datetime import datetime

from cycloan.settings import SECRET_KEY

import jwt

"""
If the user type is owner, it means owner is already logged in. So, redirect to owner dashboard.
Same for customer.
If there is no such value, then they must have logged out. Then send them to login page.
"""


class LoginView(View):
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
            json = jwt.decode(verification_token, SECRET_KEY,
                              algorithms=['HS256'])

            user_type = json['user_type']
            user_id = json['user_id']
            token_expiry = json['token_expiry']

            token_expiry = datetime.fromisoformat(token_expiry)

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
                    return redirect('login-view')

                else:
                    sql = "SELECT * FROM OWNER_EMAIL_VERIFICATION WHERE TOKEN_VALUE = %s"
                    cursor = connection.cursor()
                    cursor.execute(sql, [verification_token])
                    result = cursor.fetchall()

                    if result[0][1] == 1:
                        messages.info(request, 'You are already verified')
                        redirect('login-view')
                    
                    else:
                        print(type(result[0][5]))

                        if datetime.now() < result[0][5]:
                            print("EMAIL VERIFICATION > OWNER ")
                            print("TOKEN NOT EXPIRED")

                            sql = "UPDATE OWNER_EMAIL_VERIFICATION SET IS_VERIFIED = %s WHERE TOKEN_VALUE = %s"
                            cursor = connection.cursor()
                            cursor.execute(sql, [1, verification_token])
                            cursor.close()
                            messages.success(request, 'Hoorah ! Your account has been verified. Now you can log in.')
                        else:
                            print("Token Expired")
                            messages.error(request, "Sorry. The token is expired.")

                        return redirect('login-view')

            elif user_type == 'customer':

                sql = "SELECT COUNT(*) FROM CUSTOMER_EMAIL_VERIFICATION WHERE TOKEN_VALUE = %s"
                cursor = connection.cursor()
                cursor.execute(sql, [verification_token])
                result = cursor.fetchall()
                cursor.close()

                user_count = int(result[0][0])

                if user_count == 0:
                    messages.warning(request, 'No such accounts exists for verification. Make sure you have completed registration.')
                    return redirect('login-view')

                else:
                    sql = "SELECT * FROM CUSTOMER_EMAIL_VERIFICATION WHERE TOKEN_VALUE = %s"
                    cursor = connection.cursor()
                    cursor.execute(sql, [verification_token])
                    result = cursor.fetchall()

                    if result[0][1] == 1:
                        messages.info(request, 'You are already verified')
                        redirect('login-view')

                    else:
                        print(type(result[0][5]))
                        print(result[0][5])

                        if datetime.now() < result[0][5]:
                            print("EMAIL VERIFICATION > CUSTOMER ")
                            print("TOKEN NOT EXPIRED")

                            sql = "UPDATE CUSTOMER_EMAIL_VERIFICATION SET IS_VERIFIED = %s WHERE TOKEN_VALUE = %s"
                            cursor = connection.cursor()
                            cursor.execute(sql, [1, verification_token])
                            cursor.close()
                            messages.success(request, 'Hoorah ! Your account has been verified. Now you can log in.')
                        
                        else:
                            print("Token Expired")
                            messages.error(request, "Sorry. The token is expired.")
                        
                        return redirect('login-view')
        except:
            messages.error(request, 'Invalid verification token')
            redirect('login-view')
