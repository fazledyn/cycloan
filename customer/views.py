from django.shortcuts import render, redirect
from django.db import connection
from django.views import View
from django.contrib import messages

from .utils import save_customer_doc, save_customer_photo

CUSTOMER_ID_CONSTANT = 100


class CustomerLoginView(View):

    def get(self, request):
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
            res = result[0][0]
            if res == customer_pass:
                print('kaaj hoise')
                request.session['customer_id'] = result[0][1]
                print(request.session['customer_id'])
                return redirect('customer-dashboard-view')
            else:
                messages.error(request, 'Password mismatched. Enter correctly!')
                return redirect('login-view')

        except:
            messages.error(request, 'Your email was not found in database. Enter correctly!')
            return redirect('login-view')


class CustomerRegisterView(View):

    def get(self, request):
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

                return redirect('login-view')

            else:
                messages.warning(request, 'Account exists with similar email. Please provide different email')
                return redirect('customer-register-view')


class CustomerDashboardView(View):

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
