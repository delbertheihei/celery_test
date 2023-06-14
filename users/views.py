import csv

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Users
from tasks.async_tasks import export_users_age, export_users_name, export_users_address


class UsersView(APIView):
    pass


class ExportUsersView(APIView):

    def post(self, request):

        # 三个异步任务总用时15seconds
        users = Users.objects.all()
        export_users_name.delay(users.values('name'))
        export_users_age.delay(users.values('age'))
        export_users_address.delay(users.values('address'))

        return Response({
            'code': 200
        })
