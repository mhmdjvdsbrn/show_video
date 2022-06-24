from audioop import avg
from unicodedata import category
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Avg ,Max ,Min ,Q
from djangoflix.db.receivers import publish_state_pre_save ,unique_slugify_pre_save
from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone
from django.utils.text import slugify
from djangoflix.db.models import PublishStateOptions
from videos.models import Video
from categories.models import Category
from tags.models import TaggedItem
from ratings.models import Rating

#create Queryset model and production def ('PUBLISH' & 'timezone' < now time)
class PlaylistQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(
            state=PublishStateOptions.PUBLISH,
            publish_timestamp__lte= now 
        )

    #select search filed from models
    def Search(self ,query=None):

        if query is None:
            return self.none()
        return self.filter( 
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__title__icontains=query) |
            Q(category__slug__icontains=query) |
            Q(tags__tag__icontains=query) 
        ).distinct()

    

    #visible movie or show used in categories/views
    def movie_or_show(self):
        return self.filter(
            Q(type = Playlist.PlaylistTypeChoices.MOVIE) |
            Q(type =Playlist.PlaylistTypeChoices.SHOW)
        )


#manager model for adding to self._db & published
class PlaylistManager(models.Manager):
    def get_queryset(self):
        return PlaylistQuerySet(self.model, using=self._db)
 
    def published(self):
        return self.get_queryset().published()
    
    def featured_playlists(self):
        return self.get_queryset().filter(type=Playlist.PlaylistTypeChoices.PLAYLIST)

class Playlist(models.Model):
    class PlaylistTypeChoices(models.TextChoices):
        MOVIE = 'MOV' ,'Movie'
        SHOW = 'TVS' ,'TV Show'
        SEASONE = 'SEA' ,'Seasone'
        PLAYLIST = 'PLY' ,'Playlist'

    related = models.ManyToManyField("self", blank=True, through='PlaylistRelated') #for tabulatinline that extent playlistrelated model at playlist
    parent = models.ForeignKey("self" ,blank=True ,null=True ,on_delete = models.SET_NULL)
    category = models.ForeignKey(Category ,blank=True ,null=True ,on_delete=models.SET_NULL,related_name='playlists')
    order = models.IntegerField(default=1)
    title = models.CharField(max_length=220)
    type = models.CharField(max_length=3 ,choices=PlaylistTypeChoices.choices,
    default= PlaylistTypeChoices.PLAYLIST)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True) # 'this-is-my-video'
    video =models.ForeignKey(Video ,blank=True,null=True,related_name='playlist_featured' ,on_delete=models.SET_NULL)
    videos = models.ManyToManyField(Video,through='PlaylistItem', related_name='playlist_item', blank=True)#through , many to many fields get PlaylistItem 
    active = models.BooleanField(default=True) 
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    state = models.CharField(max_length=2, choices=PublishStateOptions.choices, default=PublishStateOptions.DRAFT)
    publish_timestamp = models.DateTimeField(auto_now_add=False, auto_now=False, blank=True, null=True)
    objects = PlaylistManager()
    #GenericRelation in playlist model
    rating = GenericRelation(Rating ,related_query_name='playlist')
    tags = GenericRelation(TaggedItem ,related_query_name='playlist')
    
    #cumputing averge 
    def get_rating_avg(self):
        return Playlist.objects.filter(id=self.id).aggregate(avrege=avg('ratings__value'))

    #cumouting max and min rate
    def get_rating_spared(self):
        return Playlist.objects.filter(id=self.id).aggregate(max=Max('ratings__value'),
            min=Min('rating__value'))

    def __str__(self) :
        return self.title

    def get_related_items(self):
        return self.playlistrelated_set.all()

    #with buttom on the movie , show ,season enters video intended
    def get_absolute_url(self):
        if self.is_movie:
            return f"/movies/{self.slug}/"
        if self.is_show:
            return f"/shows/{self.slug}/"
        if self.is_season and self.parent is not None:
            return f"/shows/{self.parent.slug}/seasons/{self.slug}/"
        return f"/playlists/{self.slug}/"


    #diagnosis that video in season
    @property
    def is_season(self):
        return self.type == self.PlaylistTypeChoices.SEASONE

    #diagnosis that video in movie
    @property
    def is_movie(self):
        return self.type == self.PlaylistTypeChoices.MOVIE

    #diagnosis that video in show
    @property
    def is_show(self):
        return self.type == self.PlaylistTypeChoices.SHOW

    #diagnosis that video active or passive
    @property
    def is_published(self):
        return self.active

    #bulid video id if video exist
    def get_movie_id(self):
        if self.video is None:
            return None
        return self.video.get_video_id()

    #published playlistitem in playlist model
    def get_clips(self): 
        return self.PlaylistItem_set.all().published()


#exp:manager for MovieProxy(type:MOVIE)
class MovieProxyManager(models.Manager):
    def all(self):
        return self.get_queryset().filter(type=Playlist.PlaylistTypeChoices.MOVIE)

#Build a subset model of the class Playlist and receive class MovieProxy 
class MovieProxy(Playlist):
    objects = MovieProxyManager()


    def get_video_id(self):
        return self.get_video_id()

    class Meta:
        verbose_name = 'Movie '
        verbose_name_plural = 'Movies'
        proxy = True
    #save to Playlist.PlaylistTypeChoices.MOVIE
    def save(self,*args,**kwargs):
        self.type = Playlist.PlaylistTypeChoices.MOVIE
        super().save(*args , **kwargs)


#manager for TVShowManager(effectless parent obj and type playlist is SHOW)
class TVShowManager(models.Manager):
    def all(self):
        return self.get_queryset().filter(parent__isnull = True,type=Playlist.PlaylistTypeChoices.SHOW)

#Build a subset model of the class Playlist and receive class TVShowManager 
class TVShowProxy(Playlist):
    objects = TVShowManager()

    class Meta:
        verbose_name = 'TV Show'
        verbose_name_plural = 'TV Shows'
        proxy = True

    #save to Playlist.PlaylistTypeChoices.MOVIE
    def save(self,*args,**kwargs):
        self.type = Playlist.PlaylistTypeChoices.SHOW
        super().save(*args , **kwargs)
    
    @property
    def seasons(self):
        return self.playlist_set.published()

    def get_short_display(self):
        return f"{self.seasons.count()} Seasons" 



class TVShowSeasonProxyManager(PlaylistManager):
    def all(self):
        return self.get_queryset().filter(parent__isnull=False, type=Playlist.PlaylistTypeChoices.SEASONE)

class TVShowSeasonProxy(Playlist):

    objects = TVShowSeasonProxyManager()

    class Meta:
        verbose_name = 'Season'
        verbose_name_plural = 'Seasons'
        proxy = True

    def save(self, *args, **kwargs):
        self.type = Playlist.PlaylistTypeChoices.SEASONE
        super().save(*args, **kwargs)

    def get_season_trailer(self):
        """
        get episodes to render for users
        """
        return self.get_video_id()

    def get_episodes(self):
        """
        get episodes to render for users
        """
        qs = self.playlistitem_set.all().published()
        print(qs)
        return qs
    




#create Queryset model and production def ('PUBLISH' & 'timezone' < now time) in general playlist and video model
class PlaylistItemQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(
            playlist__state=PublishStateOptions.PUBLISH,
            playlist__publish_timestamp__lte= now ,
            video__state=PublishStateOptions.PUBLISH,
            video__publish_timestamp__lte= now             
        )

#manager model for adding to self._db & published
class PlaylistItemManager(models.Manager):
    def get_queryset(self):
        return PlaylistItemQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = PlaylistItemManager()
    class Meta:
        ordering = ['order', '-timestamp']

#create limit choices(build by Q)
def pr_limit_choices_to():
    return Q(type=Playlist.PlaylistTypeChoices.MOVIE) |  Q(type=Playlist.PlaylistTypeChoices.SHOW)
    
#class for tabularinline in playlist admin
class PlaylistRelated(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    related = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='related_item', limit_choices_to=pr_limit_choices_to)
    order = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    
pre_save.connect(publish_state_pre_save, sender=Playlist)
pre_save.connect(unique_slugify_pre_save, sender=Playlist)

pre_save.connect(publish_state_pre_save, sender=TVShowProxy)
pre_save.connect(unique_slugify_pre_save, sender=TVShowProxy)

pre_save.connect(publish_state_pre_save, sender=MovieProxy)
pre_save.connect(unique_slugify_pre_save, sender=MovieProxy)

pre_save.connect(publish_state_pre_save, sender=TVShowSeasonProxy)
pre_save.connect(unique_slugify_pre_save, sender=TVShowSeasonProxy)





