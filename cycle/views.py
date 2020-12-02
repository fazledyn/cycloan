from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.views import View

from core.utils import check_owner
from core.utils import verify_auth_token

from .utils import save_cycle_photo

# GET   /cycle/<id>
class CycleSingleView(View):

    def get(self, request, cycle_id):

        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM CYCLE WHERE CYCLE_ID = %s"
        cursor.execute(sql, [ cycle_id ])
        cycle_count = cursor.fetchall()
        cursor.close()

        if cycle_count[0][0] == 0:
            messages.error(request, "There is no cycle with this ID.")

        else:
            cursor = connection.cursor()
            sql = "SELECT * FROM CYCLE WHERE CYCLE_ID = %s"
            cursor.execute(sql, [ cycle_id ])
            cycle = cursor.fetchall()
            cursor.close()

            cursor = connection.cursor()
            sql = "SELECT CYCLE_RATING(CYCLE_ID) FROM CYCLE WHERE CYCLE_ID = %s"
            cursor.execute(sql, [cycle_id])
            cycle_rating_list = cursor.fetchall()
            cursor.close()

            if cycle[0][2] == 0:
                cycle_status = "Free"
            elif cycle[0][2] == 1:
                cycle_status = "Reserved"

            cursor = connection.cursor()
            sql = "SELECT * FROM CYCLE_REVIEW WHERE CYCLE_ID = %s"
            cursor.execute(sql, [ cycle_id ])
            cycle_review_list = cursor.fetchall()
            cursor.close()

            context = {
                'cycle_id': cycle[0][0],
                'cycle_model': cycle[0][1],
                'cycle_status': cycle_status,
                'cycle_rating': cycle_rating_list[0][0],
                'cycle_photo': cycle[0][3],
                'cycle_owner': cycle[0][4],
                'cycle_fare_per_day': cycle[0][5],
                'cycle_review_list': cycle_review_list
            }

        return render(request, 'public_cycle.html', context)


# POST  /cycle/add/ 
class CycleAddView(View):

    @verify_auth_token
    @check_owner
    def post(self, request):
        owner_id = request.session.get('owner_id')

        # cursor = connection.cursor()
        # sql = "SELECT COUNT(*) FROM CYCLE WHERE OWNER_ID = %s"
        # cursor.execute(sql, [owner_id])
        # result = cursor.fetchall()
        # cursor.close()
        # cycle_count = int(result[0][0]) + 1 

        cycle_photo = request.FILES.get('cycle_photo')
        cycle_model = request.POST.get('cycle_model')

        cycle_photo_path = save_cycle_photo(cycle_photo, owner_id, cycle_model)

        cursor = connection.cursor()
        sql = "INSERT INTO CYCLE(CYCLE_ID, MODEL, STATUS, PHOTO_PATH, OWNER_ID, FARE_PER_DAY) VALUES(CYCLE_INCREMENT.NEXTVAL, %s, %s, %s, %s, %s)"
        cursor.execute(sql, [ cycle_model, 0, cycle_photo_path, owner_id, 1000 ])
        connection.commit()
        cursor.close()

        messages.success(request, "Cycle has been added !")
        return redirect('owner-dashboard-view')

# GET /cycle/delete/<id>
class CycleDeleteView(View):

    @verify_auth_token
    @check_owner
    def get(self, request, cycle_id):

        cursor = connection.cursor()
        sql = "DELETE FROM CYCLE WHERE CYCLE_ID = %s"
        cursor.execute(sql, [ cycle_id ])
        connection.commit()
        cursor.close()

        messages.info(request, "The cycle has been deleted.")
        return redirect('owner-dashboard-view')

