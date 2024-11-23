from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from spotify_wrapped.models import TrackModel, ArtistModel, WrapModel

from spotify_wrapped.Spotify import get_auth_url, get_access_token, get_all_info, get_user

from spotify_wrapped.helperFunc import *

def index(request):
    access_token = request.session.get("access_token", None)
    expire_time = request.session.get("expire_time", None)
    refresh_token = request.session.get("refresh_token", None)

    # If not logged in yet, show base home page
    if access_token is None or expire_time is None or refresh_token is None:
        return render(request, "spotify_wrapped/home.html", {})

    user_info = get_all_info(access_token, expire_time, refresh_token)
    print(user_info)
    if user_info["status"] == "error":
        print("failed somewhere")
        return render(request, "spotify_wrapped/home.html", {})

    return render(request, "spotify_wrapped/home.html",
                  {"user_info": user_info["value"]})

def login(request):
    return HttpResponseRedirect(get_auth_url())

def auth(request):
    auth_code = request.GET.get('code')
    access_token, expire_time, refresh_token = get_access_token(auth_code)

    request.session['access_token'] = access_token
    request.session['expire_time'] = expire_time
    request.session['refresh_token'] = refresh_token
    return HttpResponseRedirect(reverse('spotify_wrapped:index'))

def wrap(request):
    access_token = request.session.get("access_token", None)
    expire_time = request.session.get("expire_time", None)
    refresh_token = request.session.get("refresh_token", None)

    # If not logged in yet, show base home page
    if access_token is None or expire_time is None or refresh_token is None:
        return HttpResponseRedirect(reverse("spotify_wrapped:login"))

    wrap_object = get_all_info(access_token, expire_time, refresh_token)
    #new_artist = convert_artist_object_to_artist_model(wrap_object['value'].top_artists[0])
    #print(wrap_object['value'].top_tracks[0])
    #print(new_artist)
    converted_obj = convert_wrap_object_to_wrap_model(wrap_object)
    converted_obj.save()
    #print(get_all_user_wraps(wrap_object['value'].user.id))
    #print((converted_obj.top_artists.get(name = "Pink Floyd")))
    print(convert_wrap_model(converted_obj))



def logout(request):
    request.session.pop('access_token', None)
    request.session.pop('refresh_token', None)
    request.session.pop('expire_time', None)
    # spotify_logout()
    return HttpResponseRedirect(reverse('spotify_wrapped:index'))
