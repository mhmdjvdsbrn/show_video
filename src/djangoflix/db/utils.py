
import random
import string
from django.utils.text import slugify

#create rendom string 
def get_random_string(size=4, chars=string.ascii_lowercase + string.digits):
    q = "".join([random.choice(chars) for _ in range(size)])
    return q


#create unique slug for reciver functions(uniqe_sluge_pre_save)
def get_unique_slug(instance, new_slug=None, size=10, max_size=30):
    title = instance.title
    if new_slug is None:
        """
        Default
        """
        #slug = title
        slug = slugify(title)
    else:
        """
        Recursive
        """
        #reverse function(if slug was None go to Up^) 
        slug = new_slug
    # length slug until max_size=30
    slug = slug[:max_size]
    Klass = instance.__class__ #All models ,among (Playlist ,...)
    parent = None
    try:
        #register parent(parent is title moveie)
        parent = instance.parent
    except:
        pass
    #adding title (parent)
    if parent is not None:
        qs = Klass.objects.filter(parent=parent, slug=slug) 
    else:
        qs = Klass.objects.filter(slug=slug) 
    if qs.exists():
        new_slug = slugify(title) + get_random_string(size=size)
        return get_unique_slug(instance, new_slug=new_slug)
    print(instance)
    return slug

        