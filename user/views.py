from django.db import connection
from django.shortcuts import render
from django.views import View
from django.contrib import messages
from django.http import request


class OwnerPublicView(View):

    def get(self, request, owner_id):
        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM OWNER WHERE OWNER_ID = %s"
        cursor.execute(sql, [ owner_id ])
        count = cursor.fetchall()
        cursor.close()
        c = int(count[0][0])

        if c == 0:
            messages.warning(request, 'No user with this ID')
            context = {}

        else:
            cursor = connection.cursor()
            sql = "SELECT OWNER_NAME,PHOTO_PATH,OWNER_PHONE,LOCATION,EMAIL_ADDRESS,RATING FROM OWNER WHERE OWNER_ID=%s"
            cursor.execute(sql, [ owner_id ])
            result = cursor.fetchall()
            cursor.close()

            cursor = connection.cursor()
            sql = "SELECT COUNT(*) FROM CYCLE WHERE OWNER_ID = %s"
            cursor.execute(sql, [ owner_id ])
            count_cycle = cursor.fetchall()
            cursor.close()
            c_c = int(count_cycle[0][0])

            cursor = connection.cursor()
            sql = "SELECT COUNT(*) FROM PEER_REVIEW WHERE OWNER_ID = %s"
            cursor.execute(sql, [ owner_id ])
            count_peer = cursor.fetchall()
            cursor.close()
            c_p = int(count_peer[0][0])

            if c_p != 0:
                cursor = connection.cursor()
                sql = "SELECT P.CUSTOMER_ID, C.CUSTOMER_NAME, P.COMMENT_TEXT, P.RATING FROM PEER_REVIEW P, CUSTOMER C WHERE P.OWNER_ID = %s AND P.CUSTOMER_ID = C.CUSTOMER_ID"
                cursor.execute(sql, [ owner_id ])
                review_list = cursor.fetchall()
                cursor.close()
                for r in review_list:
                    reviewer_id = r[0]
                    reviewer_name = r[1]
                    comment = r[2]
                    given_rating = r[3]

            context = {
                'owner_name' : result[0][0],
                'owner_photo' : result[0][1],
                'owner_phone' : result[0][2],
                'owner_location' : result[0][3],
                'owner_email' : result[0][4],
                'owner_rating' : result[0][5]
            }

        return render(request, 'public_owner.html', context)


class CustomerPublicView(View):

    def get(self, request, customer_id):
        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM CUSTOMER WHERE CUSTOMER_ID = %s"
        cursor.execute(sql, [ customer_id ])
        count = cursor.fetchall()
        cursor.close()

        c = int(count[0][0])

        if c == 0:
            messages.warning(request, 'No user with this ID')
            context = {}

        else:
            cursor = connection.cursor()
            sql = "SELECT CUSTOMER_NAME,PHOTO_PATH,CUSTOMER_PHONE,EMAIL_ADDRESS FROM CUSTOMER WHERE CUSTOMER_ID=%s"
            cursor.execute(sql, [ customer_id ])
            result = cursor.fetchall()
            cursor.close()

            cursor = connection.cursor()
            sql = "SELECT TYPE_NAME, FILE_PATH, DESCRIPTION FROM DOCUMENT WHERE CUSTOMER_ID=%s"
            cursor.execute(sql, [ customer_id ])
            info = cursor.fetchall()
            cursor.close()

            doctype = info[0][0]
            doc_path = info[0][1]
            description = info[0][2]

            context = {
                'customer_name': result[0][0],
                'customer_photo': result[0][1],
                'customer_phone': result[0][2],
                'customer_email': result[0][3]
            }

        return render(request, 'public_customer.html', context)

