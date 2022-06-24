from django.utils import timezone
from django.utils.text import slugify
from .models import PublishStateOptions
from .utils import get_unique_slug

#if was PublishStateOptions is PUBLISH fill pubish_timestamp vacent from timezone.now()
def publish_state_pre_save(sender, instance, *args, **kwargs):
    is_publish = instance.state == PublishStateOptions.PUBLISH 
    is_draft = instance.state == PublishStateOptions.DRAFT
    if is_publish and instance.publish_timestamp is None:
        instance.publish_timestamp = timezone.now()
    elif is_draft:
        instance.publish_timestamp = None

#build slug and send models
def slugify_pre_save(sender, instance, *args, **kwargs):
    title = instance.title
    slug = instance.slug
    if slug is None:
        instance.slug = slugify(title)

#build unique slug and send models(inthereth get_unique_slug)
def unique_slugify_pre_save(sender, instance, *args, **kwargs):
    title = instance.title
    slug = instance.slug
    if slug is None:
        instance.slug = get_unique_slug(instance, size=5)