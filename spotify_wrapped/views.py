from django.http import HttpResponseRedirect
from django.shortcuts import render 
from django.urls import reverse
from.models import Feedback
import json

from spotify_wrapped.Spotify import get_auth_url, get_access_token, get_all_info


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

def slideshow(request):
    return render(request, "spotify_wrapped/slideshow.html",
                      {"slides": ["cover", "AI_Query", "albums", "artists", "genres", "mood", "popularityScore", "recommendations", "tracks"],
                   })
# start of all pages
def cover(request):
    return render(request, "spotify_wrapped/slides/cover.html", {})

def AI_Query(request):
    return render(request, "spotify_wrapped/slides/AI_Query.html", {})

def albums(request):
    return render(request, "spotify_wrapped/slides/albums.html", {})

def artists(request):
    return render(request, "spotify_wrapped/slides/artists.html", {})

def genres(request):
    return render(request, "spotify_wrapped/slides/genres.html", {})

def meetDevs(request):
    """
     View to handle 'Contact the Developers' feedback form submissions. Saves feedback to the database.

    If the request method is POST, retrieves name, email, and message from the form and stores it in the Feedback model.

    Args:
        request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
        HttpResponse: Redirects to a thank-you page after feedback is submitted, or renders the feedback form on GET request.
    """
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        Feedback.objects.create(name=name, email=email, message=message)

        context = {'success_message': 'Thank you!'}

        return render(request, "spotify_wrapped/meetDevs.html", context)
    return render(request, 'spotify_wrapped/meetDevs.html')

def mood(request):
    return render(request, "spotify_wrapped/slides/mood.html", {})

def popularityScore(request):
    return render(request, "spotify_wrapped/slides/popularityScore.html", {})

def recommendations(request):
    return render(request, "spotify_wrapped/slides/recommendations.html", {})

def tracks(request):
    return render(request, "spotify_wrapped/slides/tracks.html", {})
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


def logout(request):
    request.session.pop('access_token', None)
    request.session.pop('refresh_token', None)
    request.session.pop('expire_time', None)
    return HttpResponseRedirect(reverse('spotify_wrapped:index'))

def games(request):
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

    info_str = '{"arr": ['
    for album in user_info["value"].top_albums:
        print(album)
        info_str += '{"album": "' + album[0] + '","tracks": ['
        for track in album[1]:
            info_str += json.dumps(track.__dict__) + ","
        info_str = info_str[:-1] + "]},"
    info_str = info_str[:-1] + "]}"

    # user_info_json = json.dumps(user_info["value"])
    return render(request, "spotify_wrapped/slideshow.html", 
                  {"slides": ["games"], "user_info": info_str});
