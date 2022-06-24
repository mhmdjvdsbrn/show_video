from audioop import avg
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.db.models import Avg ,Max
User = settings.AUTH_USER_MODEL

class RatingChoices(models.IntegerChoices):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5
    __empty__ ='Unknown'

class RatingQuerySet(models.QuerySet):
    def rating(self):   
        return self.aggregate(average=Avg("value"))['average']

class RattingManager(models.Manager):
    def get_queryset(self):
        return RatingQuerySet(self.model ,using=self._db)


class Rating(models.Model):
    user = models.ForeignKey(User ,on_delete=models.CASCADE)
    value = models.IntegerField(null=True ,blank=True,
        choices=RatingChoices.choices)
    content_type = models.ForeignKey(ContentType ,
        on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type" , "object_id")
