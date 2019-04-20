from __future__ import absolute_import
from celery import shared_task
from theia.usgs import ErosWrapper

@shared_task(name='theia.locate_scenes')
def locate_scenes(imagery_request_id):
    ErosWrapper.connect()
    return

tasks = {
    'locate_scenes': locate_scenes
}
