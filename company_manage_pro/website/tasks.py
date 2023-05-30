from celery import shared_task,current_task
from . models import *


from celery import shared_task
from PIL import Image
from django.core.files.storage import default_storage


def pic_thumbnail(profile_pic_thumbnail):
    breakpoint()

    profile_pic_thumbnail_image = Image.open(profile_pic_thumbnail)
    resized_profile_pic_thumbnail = profile_pic_thumbnail_image.resize((100, 100))
    resized_profile_pic_thumbnail = resized_profile_pic_thumbnail.convert('RGB')
    return resized_profile_pic_thumbnail