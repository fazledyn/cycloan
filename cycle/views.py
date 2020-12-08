from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.views import View
from django.http import HttpResponse

from core.utils import check_owner, check_customer
from core.utils import verify_auth_token

from .utils import save_cycle_photo
from cycloan.settings import CYCLE_AVAILABLE, CYCLE_BOOKED

from cycloan.settings import TRIP_REQUESTED, TRIP_ONGOING, TRIP_REJECTED, TRIP_COMPLETED, TRIP_REVIEWED
from cycloan.settings import DLONG, DLAT
from datetime import datetime


class CycleDetailsView(View):

    def get(self, request, cycle_id):
        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM CYCLE WHERE CYCLE_ID = %s"
        cursor.execute(sql, [cycle_id])
        cycle_count = cursor.fetchall()
        cursor.close()

        if cycle_count[0][0] == 0:
            messages.error(request, "There is no cycle with this ID.")
            return redirect('index-view')

        else:
            cursor = connection.cursor()
            sql =   """
                    SELECT CYCLE_ID, PHOTO_PATH, MODEL, OWNER_ID, FARE_PER_DAY, CYCLE_RATING(CYCLE_ID)
                    FROM CYCLE
                    WHERE CYCLE_ID = %s
                    """
            cursor.execute(sql, [cycle_id])
            cycle = cursor.fetchall()
            cursor.close()

            cursor = connection.cursor()
            sql = "SELECT * FROM CYCLE_REVIEW WHERE CYCLE_ID = %s"

            sql = """
                    SELECT C.CUSTOMER_ID, C.CUSTOMER_NAME, CR.RATING, CR.COMMENT_TEXT
                    FROM CUSTOMER C, CYCLE_REVIEW CR
                    WHERE CR.CUSTOMER_ID = C.CUSTOMER_ID
                    AND CR.CYCLE_ID = %s
                """
            cursor.execute(sql, [cycle_id])
            review_list = cursor.fetchall()
            cursor.close()

            context = {
                'cycle': cycle[0],
                'review_list': review_list 
            }

            return render(request, 'cycle_details.html', context)


class CycleAddView(View):

    @verify_auth_token
    @check_owner
    def post(self, request):
        owner_id = request.session.get('owner_id')

        cycle_photo = request.FILES.get('cycle_photo')
        cycle_model = request.POST.get('cycle_model')
        cycle_fare = request.POST.get('cycle_fare')

        cycle_photo_path = save_cycle_photo(cycle_photo, owner_id, cycle_model)

        cursor = connection.cursor()
        sql = "INSERT INTO CYCLE(CYCLE_ID, MODEL, STATUS, PHOTO_PATH, OWNER_ID, FARE_PER_DAY) VALUES(CYCLE_INCREMENT.NEXTVAL, %s, %s, %s, %s, %s)"
        cursor.execute(
            sql, [cycle_model, 0, cycle_photo_path, owner_id, cycle_fare])
        connection.commit()
        cursor.close()

        messages.success(request, "Cycle has been added !")
        return redirect('owner-cycle-view')


class CycleDeleteView(View):

    @verify_auth_token
    @check_owner
    def get(self, request, cycle_id):

        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM TRIP_DETAILS WHERE STATUS = %s AND CYCLE_ID = %s"
        cursor.execute(sql, [TRIP_ONGOING, cycle_id])
        result = cursor.fetchall()
        cursor.close()

        count = int(result[0][0])

        if count == 0:
            cursor = connection.cursor()
            sql = "DELETE FROM CYCLE WHERE CYCLE_ID = %s"
            cursor.execute(sql, [cycle_id])
            connection.commit()
            cursor.close()

            messages.info(request, "The cycle has been deleted.")
            return redirect('owner-cycle-view')
        else:
            messages.info(request, "A trip is ongoing with this cycle. You can not delete this cycle.")
            return redirect('owner-cycle-view')



class RequestCycleView(View):

    @verify_auth_token
    @check_customer
    def get(self, request, cycle_id):
        customer_id = request.session.get('customer_id')
        cursor = connection.cursor()
        sql = """
                SELECT *
                FROM CYCLE C, OWNER O
                WHERE C.OWNER_ID = O.OWNER_ID
                AND C.CYCLE_ID = %s
                AND C.STATUS = %s
                """
        cursor.execute(sql, [cycle_id, CYCLE_AVAILABLE])
        cycle = cursor.fetchall()
        context = {'cycle': cycle}

        print("REQUEST CYCLE VIEW (GET) ")
        print(cycle)
        print("-------------------------------------")
        return render(request, 'request_cycle.html', context)
        
    @verify_auth_token
    @check_customer
    def post(self, request, cycle_id):
        customer_id = request.session.get('customer_id')
        customer_id = int(customer_id)

        cursor = connection.cursor()
        sql = "SELECT STATUS FROM CYCLE WHERE CYCLE_ID = %s"
        cursor.execute(sql, [cycle_id])
        status = cursor.fetchall()
        connection.commit()
        cursor.close()

        start_datetime = request.POST.get('start_datetime')
        end_datetime = request.POST.get('end_datetime')
        payment_type = request.POST.get('payment_type')

        start_datetime = datetime.fromisoformat(start_datetime)
        end_datetime = datetime.fromisoformat(end_datetime)


        if status[0][0] == CYCLE_AVAILABLE:

            cursor = connection.cursor()
            sql = "INSERT INTO TRIP_DETAILS(TRIP_ID, START_DATE_TIME, END_DATE_TIME, STATUS, PAYMENT_TYPE, CUSTOMER_ID, CYCLE_ID) VALUES(TRIP_INCREMENT.NEXTVAL, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, [start_datetime, end_datetime,
                                 TRIP_REQUESTED, payment_type, customer_id, cycle_id])
            connection.commit()
            cursor.close()

            messages.success(
                request, "Cycle requested. You'll be notified after owner confirms it.")
            return redirect('customer-dashboard-view')

        else:
            messages.warning(request, "Sorry, this cycle isn't available.")
            return redirect('customer-dashboard-view')


class ApproveCycleView(View):

    @verify_auth_token
    @check_owner
    def get(self, request, trip_id):
        owner_id = request.session.get('owner_id')
        owner_id = int(owner_id)

        cursor = connection.cursor()
        sql = "SELECT CYCLE_ID, CUSTOMER_ID FROM TRIP_DETAILS WHERE TRIP_ID = %s AND STATUS = %s"
        cursor.execute(sql, [trip_id, TRIP_REQUESTED])
        result = cursor.fetchall()
        cycle_id = result[0][0]
        customer_id = result[0][1]

        # Update the Cycle STATUS for Availability & Concurrency
        # If someone searches for a cycle by the time this view gets executed
        cursor = connection.cursor()
        sql = "UPDATE CYCLE SET STATUS = %s WHERE CYCLE_ID = %s"
        cursor.execute(sql, [CYCLE_BOOKED, cycle_id])
        connection.commit()
        cursor.close()

        # Cancelling every trip request made on this cycle which have STATUS = TRIP_REQUESTED
        cursor = connection.cursor()
        sql = "UPDATE TRIP_DETAILS SET STATUS = %s WHERE CYCLE_ID = %s AND STATUS = %s"
        cursor.execute(sql, [TRIP_REJECTED, cycle_id, TRIP_REQUESTED])
        connection.commit()
        cursor.close()

        # After cancellation, we must only approve the trip which the user had chosen.
        # Only approve the chosen trip by its TRIP_ID that we had got earlied
        cursor = connection.cursor()
        sql = "UPDATE TRIP_DETAILS SET STATUS = %s WHERE TRIP_ID = %s"
        cursor.execute(sql, [TRIP_ONGOING, trip_id])
        connection.commit()
        cursor.close()

        messages.success(request, "The cycle has been approved.")
        return redirect('owner-dashboard-view')


class CycleSearchView(View):
    def get(self, request):
        return render(request, 'cycle_search.html')

    def post(self, request):

        # CONSTANT

        customer_long = request.POST.get('customer_longtitude')
        customer_lat = request.POST.get('customer_latitude')
        preference = request.POST.get('preference')

        if preference == "Show all cycles":
            cursor = connection.cursor()
            sql = """
                        SELECT *
                        FROM CYCLE C, OWNER O
                        WHERE C.OWNER_ID = O.OWNER_ID
                        AND C.STATUS = "AVAILABLE"
                    """
            cursor.execute(sql, [])

        elif preference == "Show Nearby Cycles":
            cursor = connection.cursor()
            sql = """
                        SELECT *
                        FROM CYCLE C, OWNER O
                        WHERE C.OWNER_ID = O.OWNER_ID
                        AND ABS(O.LONGTITUDE - %s) <= %s
                        AND ABS(O.LATITUDE - %s) <= %s
                        AND C.STATUS = "AVAILABLE"
                    """
            cursor.execute(sql, [customer_long, DLONG, customer_lat, DLAT])
            result = cursor.fetchall()

            if len(result) == 0:
                print("There are no cycles to show")
                messages.info(request, "There are no cycles to show")

            else:
                print("There are cycles to show")
                context = {
                    'cycle_list': result,
                }
                return render(request, 'cycle_search.html', context)


class ReceiveCycleView(View):

    def get(self, request, trip_id):
        owner_id = request.session.get('owner_id')

        cursor = connection.cursor()
        sql =   """
                SELECT C.OWNER_ID
                FROM CYCLE C, RESERVES R
                WHERE R.CYCLE_ID = C.CYCLE_ID
                AND R.TRIP_ID = %s
                """
        cursor.execute(sql, [ trip_id ])
        result = cursor.fetchall()
        connection.commit()
        cursor.close()
        
        try:
            if owner_id == result[0][0]:
                ## yes, this trip belongs to this owner
                cursor = connection.cursor()
                sql = "UPDATE TRIP_DETAILS SET STATUS = %s WHERE TRIP_ID = %s"
                cursor.execute(sql, [ TRIP_COMPLETED, trip_id ])
                connection.commit()
                cursor.close()
                ##  the trip has been completed
                ##  now make the cycle available

                cursor = connection.cursor()
                sql =   """
                            UPDATE CYCLE
                            SET STATUS = %s
                            WHERE CYCLE_ID = (SELECT CYCLE_ID
                                            FROM TRIP_DETAILS 
                                            WHERE TRIP_ID = %s)
                        """
                cursor.execute(sql, [ CYCLE_AVAILABLE, trip_id ])
                connection.commit()
                cursor.close()

                messages.success(request, "Congrats! The trip is ended.")
                return redirect('trip-details-view', trip_id=trip_id)
                ## NOW made the cycle available
            else:
                ## not his trip
                ## send to FORBIDDEN 403
                return redirect('http-403-view')
        
        except:
            return redirect('http-404-view')

## customer
class CancelCycleView(View):
    
    def get(self, request, trip_id):
        customer_id = request.session.get('customer_id')

        cursor = connection.cursor()
        sql = "DELETE TRIP_DETAILS WHERE TRIP_ID = %s AND CUSTOMER_ID = %s AND STATUS = %s"
        cursor.execute(sql, [trip_id, customer_id, TRIP_REQUESTED])
        connection.commit()
        cursor.close()

        messages.info(request, "The cycle request has been cancelled.")
        return redirect('customer-dashboard-view')

## owner
class RejectCycleView(View):

    @check_owner
    def get(self, request, trip_id):
        owner_id = request.session.get('owner_id')
        
        cursor = connection.cursor()
        sql =   """
                UPDATE TRIP_DETAILS
                SET STATUS = %s
                WHERE TRIP_ID = %s
                """
        cursor.execute(sql, [TRIP_REJECTED, trip_id])
        connection.commit()
        cursor.close()

        messages.success(request, "Cycle request has been rejected.")
        return redirect('owner-dashboard-view')

