from django.shortcuts import render
from django.contrib import messages
from django.db import connection
from django.views import View


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
                'cycle_rating': cycle[0][3],
                'cycle_photo': cycle[0][4],
                'cycle_owner': cycle[0][5],
                'cycle_review_list': cycle_review_list 
            }

        return render(request, 'public_cycle.html', context)


# POST  /cycle/add/ 
class CycleAddView(View):

    def post(self, request):
        
        
        pass
