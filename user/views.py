from django.db import connection
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import request

from core.utils import verify_auth_token


class OwnerPublicView(View):

    @verify_auth_token
    def get(self, request, owner_id):

        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM OWNER WHERE OWNER_ID = %s"
        cursor.execute(sql, [owner_id])
        count = cursor.fetchall()
        cursor.close()
        c = int(count[0][0])

        if c == 0:
            messages.warning(request, 'No user with this ID')
            return redirect('index-view')

        else:
            cursor = connection.cursor()
            sql = "SELECT OWNER_ID, OWNER_NAME, PHOTO_PATH, OWNER_PHONE, EMAIL_ADDRESS, OWNER_RATING(OWNER_ID) FROM OWNER WHERE OWNER_ID=%s"
            cursor.execute(sql, [owner_id])
            owner = cursor.fetchall()
            cursor.close()

            cursor = connection.cursor()
            sql = "SELECT CYCLE_ID, MODEL FROM CYCLE WHERE OWNER_ID = %s"
            cursor.execute(sql, [owner_id])
            cycle_list = cursor.fetchall()
            cursor.close()

            cursor = connection.cursor()
            sql = """
                    SELECT C.CUSTOMER_ID, C.CUSTOMER_NAME, PR.RATING, PR.COMMENT_TEXT
                    FROM CUSTOMER C, PEER_REVIEW PR
                    WHERE PR.CUSTOMER_ID = C.CUSTOMER_ID
                    AND PR.OWNER_ID = %s
                    """
            cursor.execute(sql, [owner_id])
            review_list = cursor.fetchall()
            cursor.close()

            context = {
                'owner': owner[0],
                'cycle_list': cycle_list,
                'review_list': review_list
            }

            return render(request, 'owner_details.html', context)


class CustomerPublicView(View):

    @verify_auth_token
    def get(self, request, customer_id):

        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM CUSTOMER WHERE CUSTOMER_ID = %s"
        cursor.execute(sql, [customer_id])
        count = cursor.fetchall()
        cursor.close()

        c = int(count[0][0])

        if c == 0:
            messages.warning(request, 'No user with this ID')
            return redirect('index-view')

        else:
            cursor = connection.cursor()
            sql = "SELECT CUSTOMER_ID, CUSTOMER_NAME, PHOTO_PATH, CUSTOMER_PHONE, EMAIL_ADDRESS FROM CUSTOMER WHERE CUSTOMER_ID=%s"
            cursor.execute(sql, [customer_id])
            customer = cursor.fetchall()
            cursor.close()

            cursor = connection.cursor()
            sql = "SELECT TYPE_NAME, FILE_PATH FROM DOCUMENT WHERE CUSTOMER_ID=%s"
            cursor.execute(sql, [customer_id])
            doc = cursor.fetchall()
            cursor.close()

            context = {
                'customer': customer[0],
                'doc': doc[0]
            }

            return render(request, 'customer_details.html', context)


class TripDetailsView(View):

    @verify_auth_token
    def get(self, request, trip_id):
        cursor = connection.cursor()
        sql = """
                SELECT TD.TRIP_ID, TD.CYCLE_ID, C.MODEL, O.OWNER_ID, O.OWNER_NAME, CS.CUSTOMER_ID, CS.CUSTOMER_NAME, TD.START_DATE_TIME, TD.END_DATE_TIME, TD.PAYMENT_TYPE, FARE_CALCULATION(TRIP_ID), TD.STATUS
                FROM TRIP_DETAILS TD, OWNER O, CUSTOMER CS, CYCLE C
                WHERE TD.CYCLE_ID = C.CYCLE_ID
                AND C.OWNER_ID = O.OWNER_ID
                AND TD.CUSTOMER_ID = CS.CUSTOMER_ID
                AND TD.TRIP_ID = %s
                """

        cursor.execute(sql, [trip_id])
        result = cursor.fetchall()
        connection.commit()
        cursor.close()

        context = {'trip': result[0]}
        return render(request, 'trip_details.html', context)
