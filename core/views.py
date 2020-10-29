from django.shortcuts import render, redirect
from django.views import View


class LoginView(View):
    
    def get(self, request):

        name = "Admin"
        request.session['UserName'] = name
        print(request.session['UserName'])
        print('\n\n')
        print(request.session)

        return render(request, 'index.html')
