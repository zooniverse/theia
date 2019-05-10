from django.db import models as models
from django.db.models.signals import post_save
from theia.tasks import wait_for_scene
from .imagery_request import ImageryRequest


class RequestedScene(models.Model):
    scene_entity_id = models.CharField(max_length=64, null=False)
    scene_order_id = models.CharField(max_length=128, null=False)
    scene_url = models.CharField(max_length=512)
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=False)
    checked_at = models.DateTimeField(db_index=True, null=True)
    imagery_request = models.ForeignKey(ImageryRequest, related_name='requested_scenes', on_delete=models.CASCADE)

    @classmethod
    def post_save(cls, sender, instance, created, *args, **kwargs):
        if created:
            wait_for_scene.delay(instance.id)

    def __str__(self):
        return '[RequestedScene %s status %i]' % (self.scene_entity_id, self.status)


post_save.connect(RequestedScene.post_save, sender=RequestedScene)
