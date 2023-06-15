import csv

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Users
from tasks.async_tasks import export_users_age, export_users_name, export_users_address, send_mail


class UsersView(APIView):
    pass


class ExportUsersView(APIView):

    def get(self, request):
        # 提交异步任务
        ret = send_mail.delay('273323754@qq.com')

        # 获取任务结果
        print(ret, type(ret))
        # 任务是否已经执行
        print(ret.ready())
        # 任务的id
        print(ret.id)
        # 任务完成后return的内容
        print(ret.get())
        return HttpResponse('异步任务已执行')

    def post(self, request):

        # 三个异步任务总用时15seconds
        users = Users.objects.all()
        result = export_users_name.delay(users.values('name'))
        export_users_age.delay(users.values('age'))
        export_users_address.delay(users.values('address'))

        return Response({
            'code': 200
        })

