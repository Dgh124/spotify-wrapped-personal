from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from spotify_wrapped.Spotify import get_auth_url, get_access_token, get_top_tracks, get_user


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

    # So far, this only means the user is not logged in, so log them in
    if top_tracks_result["status"] == "error":
        HttpResponseRedirect(reverse('spotify_wrapped:login'))
    if user_result["status"] == "error":
        return HttpResponseRedirect(reverse('spotify_wrapped:login'))

    top_tracks = top_tracks_result["value"]
    user = user_result["value"]
    return render(request, "spotify_wrapped/home.html",
                  {"top_tracks": top_tracks, "user": user})

# start of all pages
def cover(request):
    return render(request, "spotify_wrapped/cover.html", {})

def AI_Query(request):
    return render(request, "spotify_wrapped/AI_Query.html", {})

def albums(request):
    return render(request, "spotify_wrapped/albums.html", {})

def artists(request):
    return render(request, "spotify_wrapped/artists.html", {})

def genres(request):
    return render(request, "spotify_wrapped/genres.html", {})

def meetDevs(request):
    return render(request, "spotify_wrapped/meetDevs.html", {})

def mood(request):
    return render(request, "spotify_wrapped/mood.html", {})

def popularityScore(request):
    return render(request, "spotify_wrapped/popularityScore.html", {})

def recommendations(request):
    return render(request, "spotify_wrapped/recommendations.html", {})

def tracks(request):
    return render(request, "spotify_wrapped/tracks/html", {})
# end of all pages

def login(request):
    return HttpResponseRedirect(get_auth_url())

def auth(request):
    auth_code = request.GET.get('code')
    access_token, expire_time, refresh_token = get_access_token(auth_code)

    request.session['access_token'] = access_token
    request.session['expire_time'] = expire_time
    request.session['refresh_token'] = refresh_token
    return HttpResponseRedirect(reverse('spotify_wrapped:index'))



