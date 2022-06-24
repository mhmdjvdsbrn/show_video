from django.shortcuts import render
from django.views.generic import ListView,DetailView
from .models import MovieProxy ,TVShowProxy ,TVShowSeasonProxy ,Playlist
from django.http import Http404
from django.utils import timezone
from djangoflix.db.models import PublishStateOptions
from .mixins import PlaylistMixin


class SearchView(PlaylistMixin ,ListView):
    def get_context_data(self):
        context = super().get_context_data()
        query = self.request.GET.get("q")
        if query is not None:
            context['title'] = f"Searcned for {query}"
        else:
            context['title'] = f"Perform a search"
        return context

    #* get search field from user in the from of dictionary {} (My acquaintance is  django)
    def get_queryset(self):
        query =self.request.GET.get("q") #*
        return Playlist.objects.all().movie_or_show().Search(query=query)   



#render Movie list from MovieProxy and Combine PlaylistMixin,ListView      
class MovieListView(PlaylistMixin,ListView):
    queryset = MovieProxy.objects.all()
    title = 'Movies'

#render Movie detail from MovieProxy and Combine PlaylistMixin,DetailView      
class MovieDetailView(PlaylistMixin, DetailView):
    template_name = 'playlists/movie_detail.html'
    queryset = MovieProxy.objects.all()


#render playlist detail from playlist and Combine PlaylistMixin,DetailView 
class PlaylistDetailView(PlaylistMixin, DetailView):
    template_name = 'playlists/playlist_detail.html'
    queryset = Playlist.objects.all()



#render TVShow list from TVShowProxy and Combine PlaylistMixin,ListView 
class TVShowListView(PlaylistMixin,ListView):
    queryset = TVShowProxy.objects.all()
    title = 'TV Shows'

#render TVShowDetailView list from TVShowProxy and Combine PlaylistMixin,DeatilView
class TVShowDetailView(PlaylistMixin, DetailView):
    template_name = 'playlists/tvshow_detail.html'
    queryset = TVShowProxy.objects.all()



#render TVShowSeasonDetailView list from TVShowProxy and Combine PlaylistMixin,DetailView 
class TVShowSeasonDetailView(PlaylistMixin, DetailView):
    template_name = 'playlists/season_detail.html'
    queryset = TVShowSeasonProxy.objects.all()
    
    def get_object(self):
        kwargs = self.kwargs
        show_slug = kwargs.get("showSlug")
        season_slug = kwargs.get("seasonSlug")
        now = timezone.now()
        try:
            obj = TVShowSeasonProxy.objects.get(
                state=PublishStateOptions.PUBLISH,
                publish_timestamp__lte=now,
                parent__slug__iexact=show_slug,
                slug__iexact=season_slug
            )
        except TVShowSeasonProxy.MultipleObjectsReturned:
            qs = TVShowSeasonProxy.objects.filter(
                parent__slug__iexact=show_slug,
                slug__iexact=season_slug
            ).published()
            obj = qs.first()
            # log this
        except:
            raise Http404
        return obj


        # qs = self.get_queryset().filter(parent__slug__iexact=show_slug, slug__iexact=season_slug)
        # if not qs.count() == 1:
        #     raise Http404
        # return qs.first()


#render FeaturedPlaylist list from Playlist and Combine PlaylistMixin,ListView 
class FeaturedPlaylistListView(PlaylistMixin,ListView):
    template_name = 'playlists/faetured_list.html'
    queryset = Playlist.objects.featured_playlists()
    title = 'featured'


