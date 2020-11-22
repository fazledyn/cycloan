from django.shortcuts import render, redirect
from django.db import connection
from django.views import View
from django.contrib import messages

from .utils import save_customer_doc, save_customer_photo
from core.utils import create_auth_token

## decorators
from core.utils import verify_auth_token, check_customer

class CustomerLoginView(View):

    def get(self, request):
        if request.session.get('auth_token'):
            return redirect('owner-dashboard-view')
        return redirect('login-view')

    def post(self, request):
        customer_email = request.POST.get('customer-email')
        customer_pass = request.POST.get('customer-password')

        cursor = connection.cursor()
        sql = "SELECT PASSWORD, CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ADDRESS=%s"
        cursor.execute(sql, [customer_email])
        result = cursor.fetchall()
        cursor.close()

        try:
            fetched_pass = result[0][0]
            if fetched_pass == customer_pass:
                customer_id = result[0][1]

                request.session['customer_id'] = customer_id
                request.session['auth_token'] = create_auth_token(customer_id)
                request.session['user_type'] = 'customer'
                
                return redirect('customer-dashboard-view')
            else:
                messages.error(request, 'Password mismatched. Enter correctly!')
                return redirect('login-view')

        except:
            messages.error(request, 'Your email was not found in database. Enter correctly!')
            return redirect('login-view')


class CustomerLogoutView(View):
    
    @verify_auth_token
    @check_customer
    def get(self, request):
        request.session.pop('customer_id', None)    
        request.session.pop('user_type', None)
        request.session.pop('auth_token', None)
        messages.info(request, 'You are logged out.')
        return redirect('login-view')


class CustomerRegisterView(View):

    def get(self, request):
        if request.session.get('auth_token'):
            return redirect('owner-dashboard-view')
        return render(request, 'customer_register.html')

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
            return redirect('customer-register-view')
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
                customer_id = 101 + count
                photo_path = save_customer_photo(photo, customer_id)
                doc_path = save_customer_doc(document, customer_id)

                cursor = connection.cursor()
                sql = "INSERT INTO CUSTOMER(CUSTOMER_ID,CUSTOMER_NAME,PASSWORD,CUSTOMER_PHONE,PHOTO,EMAIL_ADDRESS) VALUES(%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, [customer_id, fullname, password, contact, photo_path, email])
                connection.commit()
                cursor.close()

                cursor = connection.cursor()
                sql = "INSERT INTO DOCUMENT(CUSTOMER_ID,TYPE_NAME,FILE_NAME) VALUES(%s, %s, %s)"
                cursor.execute(sql, [customer_id, doctype, doc_path])
                connection.commit()
                cursor.close()

                cursor = connection.cursor()
                sql = "INSERT INTO CUSTOMER_EMAIL_VERIFICATION(CUSTOMER_ID,IS_VERIFIED,EMAIL_ADDRESS) VALUES(%s, %s, %s)"
                cursor.execute(sql, [customer_id, 0, email])
                connection.commit()
                cursor.close()

                messages.success(request, 'Account create successful. Now you can login.')
                return redirect('login-view')

            else:
                messages.warning(request, 'Account exists with similar email. Please provide different email')
                return redirect('customer-register-view')


class CustomerDashboardView(View):

    @verify_auth_token
    @check_customer
    def get(self, request):
        customer_id = request.session.get('customer_id')
        cursor = connection.cursor()
        sql = "SELECT CUSTOMER_NAME FROM CUSTOMER WHERE CUSTOMER_ID=%s"
        cursor.execute(sql, [customer_id])
        result = cursor.fetchall()
        cursor.close()
        customer_name = result[0][0]
        print(customer_name)
        context = {'customer_name': customer_name}
        return render(request, 'customer_dashboard.html', context)


class CustomerProfileView(View):

    @verify_auth_token
    @check_customer
    def get(self, request):
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
        
        
        #####################   WORK LEFT   ####################
        ########################################################

        """
        :: Customer Profile Data Update
        > Can upload new photo here
        > Can update the phone number
        > Can update the name ??? (not sure)
        """

        """
        ? Password Change:
        Get current password through the form.
        `request.POST.get('old_password)`

        Then get new password
        `request.POST.get('new_password)`
        `request.POST.get('new_password_confirm')`

        FlowChart:

        If the old password matches with the DATABASE, then check the new ones (constraints also)
        If both of them match, then over-write the new password(hash) in the database.
                
        """

        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password_confirm = request.POST.get('new_password_confirm')

        customer_new_phone = request.POST.get('customer_new_phone')
        customer_new_photo = request.FILES.get('customer_new_photo')

        old_password_from_db = result[0][0]

        if (old_password == "" and new_password == "" and new_password_confirm == ""):
            # do other changes
        
        else:
            
            if (new_password == new_password_confirm):
                if (old_password == old_password_from_db):
                    pass
                    ### change the password and return to new page.
                else:
                    messages.error('Your current password is not correct!')
            else:
                messages.error('The new passwords do not match! Type carefully.')
                return redirect('customer-profile-view')



