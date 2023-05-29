# import necessary libraries
from datetime import date
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import *

def send_birthday_wishes():
    today = date.today().strftime("%m-%d")
    employees = Employees_table.objects.filter(date_of_birth=today)
    print(employee)
    print(today)
    for employee in employees:

        email = EmailMessage(
            subject="It's your birthday today",
            body=f"Dear {employee.first_name},\n\nHappy Birthday! Wishing you a fantastic day filled with joy and celebration.\n\nBest regards.",
            to=[employees.email],
        )
        email.send()
    