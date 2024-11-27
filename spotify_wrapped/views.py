from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from.models import Feedback
import json

from spotify_wrapped.Spotify import get_auth_url, get_access_token, get_all_info
from spotify_wrapped.modelControllers import *


def slideshow(request):
    access_token = request.session.get("access_token", None)
    expire_time = request.session.get("expire_time", None)
    refresh_token = request.session.get("refresh_token", None)

    # If not logged in yet, show base home page
    if access_token is None or expire_time is None or refresh_token is None:
        return render(request, "spotify_wrapped/slideshow.html", {})

    user_info = get_all_info(access_token, expire_time, refresh_token)

    if user_info["status"] == "error":
        print("failed somewhere")
        return render(request, "spotify_wrapped/slideshow.html", {})

    return render(request, "spotify_wrapped/slideshow.html", {
        "user_info": user_info["value"],
        # "slides": ["games"],
        "slides": ["cover", "mood", "AI_Query", 
                   "artists", "genres", "albums", 
                   "popularityScore", "recommendations", "tracks", "games",]
    })
    # Adolfo: artists, personality, albums, mood, genres, pop score, recommended, reciept


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


def logIn(request):
    context = {"url": get_auth_url()}
    return render(request, "spotify_wrapped/logIn.html", context)

def profile(request):
    access_token = request.session.get("access_token", None)
    expire_time = request.session.get("expire_time", None)
    refresh_token = request.session.get("refresh_token", None)

    # If not logged in yet, show login page
    if access_token is None or expire_time is None or refresh_token is None:
        return HttpResponseRedirect(reverse('spotify_wrapped:login'))

    return render(request, "spotify_wrapped/profile.html", {})

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

    #spotify.py wrap object
    wrap_object = get_all_info(access_token, expire_time, refresh_token)

    #models wrap model
    converted_obj = convert_wrap_object_to_wrap_model(wrap_object)
    converted_obj.save()

    #spotify.py wrap object
    print(convert_wrap_model(converted_obj))


def logout(request):
    request.session.pop('access_token', None)
    request.session.pop('refresh_token', None)
    request.session.pop('expire_time', None)
    return HttpResponseRedirect(reverse('spotify_wrapped:index'))

