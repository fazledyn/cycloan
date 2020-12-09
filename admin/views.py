from django.db import connection
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.http import request

from core.utils import create_auth_token, verify_auth_token
from .utils import check_admin
from cycloan.settings import TRIP_COMPLETED, TRIP_ONGOING, TRIP_REJECTED, TRIP_REVIEWED, TRIP_REQUESTED

import hashlib


class AdminLoginView(View):
    
    def get(self, request):
        return render(request, 'admin_login.html')

    def post(self, request):
        admin_email = request.POST.get('admin-email')
        admin_pass = request.POST.get('admin-password')

        print(admin_email)
        print(admin_pass)

        cursor = connection.cursor()
        sql = "SELECT ADMIN_PASSWORD, ADMIN_ID, ADMIN_NAME, ADMIN_EMAIL FROM ADMIN WHERE ADMIN_EMAIL=%s"
        cursor.execute(sql, [admin_email])
        result = cursor.fetchall()
        cursor.close()

        print(result)

        try:
            fetched_pass = result[0][0]
            #   hashed_admin_password = hashlib.sha256(admin_pass.encode()).hexdigest()
            hashed_admin_password = admin_pass

            if fetched_pass == hashed_admin_password:
                request.session['admin_id'] = result[0][1]
                request.session['auth_token'] = create_auth_token(user_id=result[0][1])
                request.session['user_type'] = 'admin'
                request.session['user_email'] = result[0][3]
                request.session['user_name'] = result[0][2]

                return redirect('admin-dashboard-view')
        
            else:
                messages.error(request, 'Password did not match. Enter correctly!')
                return redirect('admin-login-view')

        except:
            messages.error(request,'Your email address is not found in our database. Enter it correctly!')
            return redirect('admin-login-view')


class AdminLogoutView(View):

    @verify_auth_token
    @check_admin
    def get(self, request):
        request.session.pop('admin_id', None)
        request.session.pop('auth_token', None)
        request.session.pop('user_type', None)
        request.session.pop('user_email', None)
        request.session.pop('user_name', None)
        
        messages.info(request, "You are logged out.")
        return redirect('admin-login-view')


class AdminDashboardView(View):
    
    @verify_auth_token
    @check_admin
    def get(self, request):

        cursor = connection.cursor()
        sql = "SELECT SUM(FARE_CALCULATION(TRIP_ID)) FROM TRIP_DETAILS WHERE (STATUS = %s OR STATUS = %s)"
        cursor.execute(sql, [ TRIP_COMPLETED, TRIP_REVIEWED ])
        total_fare = cursor.fetchall()[0][0]
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM TRIP_DETAILS WHERE (STATUS = %s OR STATUS = %s)"
        cursor.execute(sql, [ TRIP_COMPLETED, TRIP_REVIEWED ])
        total_trip = cursor.fetchall()[0][0]
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM CUSTOMER"
        cursor.execute(sql, [])
        total_customer = cursor.fetchall()[0][0]
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM OWNER"
        cursor.execute(sql, [])
        total_owner = cursor.fetchall()[0][0]
        connection.commit()
        cursor.close()
        
        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM CYCLE"
        cursor.execute(sql, [])
        total_cycle = cursor.fetchall()[0][0]
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        sql = "SELECT SUM( (END_DATE_TIME - START_DATE_TIME) * 24) FROM TRIP_DETAILS"
        cursor.execute(sql, [])
        total_time = cursor.fetchall()[0][0]
        total_time = round(total_time, 2)
        connection.commit()
        cursor.close()

        context = {
            'total_fare': total_fare,
            'total_trip': total_trip,
            'total_time': total_time,
            'total_cycle':total_cycle,
            'total_owner': total_owner,
            'total_customer': total_customer
        }

        return render(request, 'admin_dashboard.html', context)


class CycleListView(View):

    @verify_auth_token
    @check_admin
    def get(self, request):
        cursor = connection.cursor()
        sql = "SELECT CYCLE_ID, MODEL, FARE_PER_DAY FROM CYCLE"
        cursor.execute(sql)
        cycle_list = cursor.fetchall()
        cursor.close()

        context = { 'list': cycle_list }
        return render(request, 'cycle_list.html', context)


class OwnerListView(View):
    
    @verify_auth_token
    @check_admin
    def get(self, request):
        cursor = connection.cursor()
        sql = "SELECT OWNER_ID, OWNER_NAME, OWNER_PHONE, EMAIL_ADDRESS FROM OWNER"
        cursor.execute(sql)
        owner_list = cursor.fetchall()
        cursor.close()
        
        context = { 'list': owner_list }
        return render(request, 'owner_list.html', context)


class CustomerListView(View):
    
    @verify_auth_token
    @check_admin
    def get(self, request):
        cursor = connection.cursor()
        sql = "SELECT CUSTOMER_ID, CUSTOMER_NAME, CUSTOMER_PHONE, EMAIL_ADDRESS FROM CUSTOMER "
        cursor.execute(sql)
        customer_list = cursor.fetchall()
        cursor.close()

        context = { 'list': customer_list }
        return render(request, 'customer_list.html', context)


class TripListView(View):

    @verify_auth_token
    @check_admin
    def get(self, request):
        cursor = connection.cursor()
        sql = "SELECT TRIP_ID, START_DATE_TIME, END_DATE_TIME, STATUS, FARE_CALCULATION(TRIP_ID) FROM TRIP_DETAILS"
        cursor.execute(sql, [])
        trip_list = cursor.fetchall()
        cursor.close()

        context = { 'list': trip_list }
        return render(request, 'trip_list.html', context)


class AdminRegisterView(View):

    def get(self, request):
        return render(request, 'admin_register.html')

    def post(self, request):
    
        fullname = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.warning(request, 'Passwords do not match. Check again')
            return redirect('admin-register-view')
            
        else:
            cursor = connection.cursor()
            sql = "SELECT COUNT(*) FROM ADMIN WHERE ADMIN_EMAIL=%s"
            cursor.execute(sql, [email])
            result = cursor.fetchall()
            cursor.close()
            count = int(result[0][0])
            
            if count == 0:
                # hashed_password = hashlib.sha256(password.encode()).hexdigest()
                hashed_password = password

                cursor = connection.cursor()
                sql = "INSERT INTO ADMIN(ADMIN_ID,ADMIN_NAME,ADMIN_EMAIL,ADMIN_PASSWORD) VALUES(ADMIN_INCREMENT.NEXTVAL, %s, %s, %s)"
                cursor.execute(sql, [fullname, email, hashed_password])
                connection.commit()
                cursor.close()

                messages.success(request, 'Successfully created admin account.')
                return redirect('admin-dashboard-view')

            else:
                messages.warning(request, 'Account exists with similar email. Please provide different email')
                return redirect('admin-register-view')
