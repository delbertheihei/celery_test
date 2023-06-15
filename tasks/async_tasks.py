from .task import app
import csv
import time
from users.models import Users


@app.task
def export_users_name(users):

    time.sleep(10)

    with open('users_name.csv', 'w', encoding='utf8') as f:
        user_csv = csv.DictWriter(f, fieldnames=['name'])
        user_csv.writeheader()
        for user in users:
            user_csv.writerow(user)
    return


@app.task
def export_users_age(users):

    time.sleep(5)
    with open('users_age.csv', 'w', encoding='utf8') as f:
        user_csv = csv.DictWriter(f, fieldnames=['age'])
        user_csv.writeheader()
        for user in users:
            user_csv.writerow(user)
    return


@app.task
def export_users_address(users):

    time.sleep(10)
    with open('users_address.csv', 'w', encoding='utf8') as f:
        user_csv = csv.DictWriter(f, fieldnames=['address'])
        user_csv.writeheader()
        for user in users:
            user_csv.writerow(user)
    return


@app.task
def send_mail(email):
    print(f'向{email}发送邮件！')
    time.sleep(5)
    print('发送完成')
    return '邮件发送成功 OK'
