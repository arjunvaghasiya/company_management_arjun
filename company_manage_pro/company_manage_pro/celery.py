from __future__ import absolute_import,unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab
os.environ.setdefault('DJANGO_SETTINGS_MODULE','company_manage_pro.settings')

app  = Celery('company_manage_pro')
app.conf.enable_utc = False
app.conf.update(timezone = 'Asia/Kolkata')
app.config_from_object('django.conf:settings',namespace='CELERY')
app.autodiscover_tasks()

# app.conf.beat_schedule = {

#     'Top-update-at-every-two-minutes':{
#         'task' : 'website.tasks.pic_thumbnail',
#         'schedule' : crontab(minute='*/2'),
#     },

# }

app.conf.update(CELERY_ACCEPT_CONTENT=["json"],
                CELERY_TASK_SERIALIZER="json",
                CELERY_RESULT_SERIALIZER="json")
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 