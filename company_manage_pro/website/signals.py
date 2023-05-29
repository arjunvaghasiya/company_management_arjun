from django.contrib.auth.models import User
from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
import os

@receiver(post_save, sender=User)
def create_profile_user(sender, instance, created, **kwargs):
    if created:
        user_profile = Companies_table.objects.create(user=instance)
        user_profile.save()

@receiver(post_save, sender=Employees_table)
def create_jwt_token(sender, instance=None, created=False, **kwargs):
    if created:
        refresh = RefreshToken.for_user(instance)
        instance.jwt_token = str(refresh.access_token)
        instance.save()
        
@receiver(pre_delete, sender=Companies_table)
def delete_related_employees(sender, instance, **kwargs):

    employees = Employees_table.objects.filter(company=instance)
    employees.delete()
    
    
@receiver(pre_delete, sender=Employees_table)
def delete_related_employees(sender, instance, **kwargs):
    company_id = instance.fk_company_id
    try:
        company = Companies_table.objects.get(company_id=company_id)
        if instance.profile_pic:
            if os.path.isfile(instance.profile_pic.path):
                os.remove(instance.profile_pic.path)
        if instance.profile_pic_thumbnail:
            if os.path.isfile(instance.profile_pic_thumbnail.path):
                os.remove(instance.profile_pic_thumbnail.path)
        company.company_total_employees -= 1
        company.save()
    except Companies_table.DoesNotExist:
        return

  

