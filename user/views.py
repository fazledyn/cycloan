from django.db import connection
from django.shortcuts import render
from django.views import View
from django.contrib import messages
from django.http import request


class OwnerPublicView(View):

    def get(self, request):
        owner_id = request.POST.get('owner_id')
        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM OWNER WHERE OWNER_ID = %s"
        cursor.execute(sql, owner_id)
        count = cursor.fetchall()
        cursor.close()
        c = int(count[0][0])
        
        if c == 0:
            messages.warning(request, 'No user with this ID')
        
        else:
            cursor = connection.cursor()
            sql = "SELECT OWNER_NAME,PHOTO_PATH,OWNER_PHONE,LOCATION,EMAIL_ADDRESS,RATING FROM OWNER WHERE OWNER_ID=%s"
            cursor.execute(sql, [owner_id])
            result = cursor.fetchall()
            cursor.close()

            name = result[0][0]
            photo_path = result[0][1]
            phone = result[0][2]
            location = result[0][3]
            email = result[0][4]
            owner_rating = result[0][5]

            cursor = connection.cursor()
            sql = "SELECT PHOTO,MODEL,RATING FROM CYCLE WHERE OWNER_ID = %s"
            cursor.execute(sql, owner_id)
            cycle = cursor.fetchall()
            cursor.close()
        
            for c in cycle:
                cycle_photo_path = cycle[0]
                model = cycle[1]
                cycle_rating = cycle[3]

            cursor = connection.cursor()
            sql = "SELECT P.CUSTOMER_ID, C.CUSTOMER_NAME, P.COMMENT_TEXT, P.RATING FROM PEER_REVIEW P, CUSTOMER C WHERE P.OWNER_ID = %s AND P.CUSTOMER_ID = C.CUSTOMER_ID"
            cursor.execute(sql, [owner_id])
            review_list = cursor.fetchall()
            cursor.close()
        
            for r in review_list:
                reviewer_id = review_list[0]
                reviewer_name = review_list[1]
                comment = review_list[2]
                given_rating = review_list[3]


class CustomerPublicView(View):
    
    def get(self, request):
        customer_id = request.POST.get('customer_id')
        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM CUSTOMER WHERE CUSTOMER_ID = %s"
        cursor.execute(sql, customer_id)
        count = cursor.fetchall()
        cursor.close()

        c = int(count[0][0])
        
        if c == 0:
            messages.warning(request, 'No user with this ID')
        
        else:
            cursor = connection.cursor()
            sql = "SELECT CUSTOMER_NAME,PHOTO_PATH,CUSTOMER_PHONE,EMAIL_ADDRESS FROM CUSTOMER WHERE CUSTOMER_ID=%s"
            cursor.execute(sql, [customer_id])
            result = cursor.fetchall()
            cursor.close()
            name = result[0][0]
            photo_path = result[0][1]
            phone = result[0][2]
            email = result[0][3]

            cursor = connection.cursor()
            sql = "SELECT TYPE_NAME,FILE_NAME,DESCRIPTION FROM DOCUMENT WHERE CUSTOMER_ID=%s"
            cursor.execute(sql, [customer_id])
            info = cursor.fetchall()
            cursor.close()

            doctype = info[0][0]
            doc_path = info[0][1]
            description = info[0][2]


class CyclePublicView(View):
    def get(self, request):
        cycle_id = request.POST.get('cycle_id')
        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM CYCLE WHERE CYCLE_ID = %s"
        cursor.execute(sql, cycle_id)
        count = cursor.fetchall()
        cursor.close()
        
        c = int(count[0][0])
        
        if c == 0:
            messages.warning(request, 'No cycle with this ID')
        else:
            cursor = connection.cursor()
            sql = "SELECT PHOTO,MODEL,STATUS,RATING,OWNER_ID FROM CYCLE WHERE CYCLE_ID = %s"
            cursor.execute(sql, [cycle_id])
            result = cursor.fetchall()
            cursor.close()

            photo_path = result[0][0]
            model = result[0][1]
            status = result[0][2]
            cycle_rating = result[0][3]
            owner_id = result[0][4]

            cursor = connection.cursor()
            sql = "SELECT CR.CUSTOMER_ID, C.CUSTOMER_NAME, CR.COMMENT_TEXT, CR.RATING FROM CYCLE_REVIEW CR, CUSTOMER C WHERE CR.CYCLE_ID = %s AND CR.CUSTOMER_ID = C.CUSTOMER_ID "
            cursor.execute(sql, [cycle_id])
            review_list = cursor.fetchall()
            cursor.close()

            for r in review_list:
                reviewer_id = review_list[0]
                reviewer_name = review_list[1]
                comment = review_list[2]
                given_rating = review_list[3]

def test(request):
    if request.method == "GET":
        return render(request, 'customer_public.html')
    