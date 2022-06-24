from django.contrib import admin
from .models import Video, VideoAllProxy, VideoManager ,VideoPublishedProxy
from playlists.models import Playlist , PlaylistItem 

class PlaylistItemInline(admin.TabularInline):
    extra = 0
    model = PlaylistItem

class VideoAllAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'video_id' ,'is_published', 'state', 'publish_timestamp','get_playlist_ids']
    search_fields = ['title']
    readonly_fields = ['id','is_published','publish_timestamp','get_playlist_ids']
    list_filter = ['active','state']
    inlines = [PlaylistItemInline]
    class Meta:
        model = VideoAllProxy

admin.site.register(VideoAllProxy ,VideoAllAdmin)


class VideoPublishedProxyAdmin(admin.ModelAdmin):
    list_display = ['title', 'video_id']
    search_fields = ['title']
    class Meta:
        model = VideoPublishedProxy 
        
    def get_queryset(self, request):
        return VideoPublishedProxy.objects.filter(active=True)

admin.site.register(VideoPublishedProxy ,VideoPublishedProxyAdmin )

# Register your models here.
