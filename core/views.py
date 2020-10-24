from django.shortcuts import render
from django.db import connection

def insert_admin(request):
    if request.method == 'GET':
        cursor = connection.cursor()
        sql = "INSERT INTO ADMIN VALUES(%s,%s,%s)"
        cursor.execute(sql, [101, 'purba@gmail.com', 'purbasha21'])
        connection.commit()
        cursor.close()
        cursor = connection.cursor()
        sql = "SELECT * FROM ADMIN"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()

        dict_result = []

        for r in result:
            admin_id = r[0]
            admin_email = r[1]
            admin_pass = r[2]
            row = {'admin_id': admin_id, 'admin_email': admin_email, 'admin_pass': admin_pass}
            dict_result.append(row)

        # return render(request,'list_jobs.html',{'jobs' : Job.objects.all()})
        return render(request, 'login.html', {'admins': dict_result})

