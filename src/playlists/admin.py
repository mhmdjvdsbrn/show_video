from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import MovieProxy, PlaylistRelated, Playlist , PlaylistItem ,TVShowProxy ,TVShowSeasonProxy ,TaggedItem
from tags.admin import TaggedItemInline


#show admin movieproxy
class MovieProxyAdmin(admin.ModelAdmin):
    inlines = [TaggedItemInline]
    list_display = ['title']
    fields = ['title', 'description', 'state', 'category', 'video', 'slug']
    class Meta:
        model = MovieProxy

    def get_queryset(self, request):
        return MovieProxy.objects.all()

admin.site.register(MovieProxy, MovieProxyAdmin)


class SeasonEpisodeInline(admin.TabularInline):
    model = PlaylistItem
    extra = 0

class TVShowSeasonProxyAdmin(admin.ModelAdmin):
    inlines = [TaggedItemInline, SeasonEpisodeInline]
    list_display = ['title', 'parent']
    class Meta:
        model = TVShowSeasonProxy
    
    def get_queryset(self, request):
        return TVShowSeasonProxy.objects.all()

admin.site.register(TVShowSeasonProxy, TVShowSeasonProxyAdmin)


class TVShowSeasonProxyInline(admin.TabularInline):
    model = TVShowSeasonProxy
    extra = 0
    fields = ['order', 'title', 'state']

class TVShowProxyAdmin(admin.ModelAdmin):
    inlines = [TaggedItemInline, TVShowSeasonProxyInline]
    list_display = ['title']
    fields = ['title', 'description', 'state', 'category', 'video', 'slug']
    class Meta:
        model = TVShowProxy
    
    def get_queryset(self, request):
        return TVShowProxy.objects.all()

admin.site.register(TVShowProxy, TVShowProxyAdmin)



#create & adding playlistrelated in playlist admin
class PlaylistRelatedItemInline(admin.TabularInline):
    model = PlaylistRelated
    extra = 0
    fk_name = 'playlist' #select one of foreignkey in playlistrelated

class PlaylistItemInline(admin.TabularInline):
    extra = 0
    model = PlaylistItem

class PlaylistAdmin(admin.ModelAdmin):
    inlines =[PlaylistItemInline ,PlaylistRelatedItemInline ,TaggedItemInline]
    class Meta:
       model = Playlist 
       fields = [
        'title',
        'description',
        'slug',
        'state',
        'active'
       ]

    def get_queryset(self, request):
        return Playlist.objects.filter(type = Playlist.PlaylistTypeChoices.PLAYLIST )

admin.site.register(Playlist,PlaylistAdmin)

