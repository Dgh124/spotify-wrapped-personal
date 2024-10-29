from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from spotify_wrapped.Spotify import (get_auth_url, get_access_token, get_top_tracks, get_user,
                                     get_top_track_audio_link, get_suggested_genres, get_top_artists)


def index(request):
    access_token = request.session.get("access_token", None)
    expire_time = request.session.get("expire_time", None)
    refresh_token = request.session.get("refresh_token", None)

    # If not logged in yet, show base home page
    if access_token is None or expire_time is None or refresh_token is None:
        return render(request, "spotify_wrapped/home.html", {})

    top_tracks_result = get_top_tracks(
        access_token=access_token, expires_at=expire_time, refresh_token=refresh_token,
    )
    user_result = get_user(
        access_token=access_token, expires_at=expire_time, refresh_token=refresh_token,
    )
    # Unpack tuple returned by get_top_artists
    top_artists_result, top_genres = get_top_artists(
        access_token=access_token, expires_at=expire_time, refresh_token=refresh_token,
    )

    # So far, this only means the user is not logged in, so log them in
    if top_tracks_result["status"] == "error":
        return HttpResponseRedirect(reverse('spotify_wrapped:login'))
    if user_result["status"] == "error":
        return HttpResponseRedirect(reverse('spotify_wrapped:login'))
    if top_artists_result["status"] == "error":
        return HttpResponseRedirect(reverse('spotify_wrapped:login'))

    print(top_tracks_result)
    top_tracks = top_tracks_result["value"]
    user = user_result["value"]
    audio_link = get_top_track_audio_link(top_tracks)
    top_artists = top_artists_result["value"]
    # Get suggested genres
    suggested_genres = get_suggested_genres(access_token)
    print(top_genres)



    return render(request, "spotify_wrapped/home.html",
                  {"top_tracks": top_tracks, "user": user, "audio_link": audio_link,
                   "top_artists": top_artists, "top_genres": top_genres, "suggested_genres": suggested_genres})

def login(request):
    return HttpResponseRedirect(get_auth_url())

def auth(request):
    auth_code = request.GET.get('code')
    access_token, expire_time, refresh_token = get_access_token(auth_code)

    request.session['access_token'] = access_token
    request.session['expire_time'] = expire_time
    request.session['refresh_token'] = refresh_token
    return HttpResponseRedirect(reverse('spotify_wrapped:index'))


def logout(request):
    request.session.pop('access_token', None)
    request.session.pop('refresh_token', None)
    request.session.pop('expire_time', None)
    # spotify_logout()
    return HttpResponseRedirect(reverse('spotify_wrapped:index'))
