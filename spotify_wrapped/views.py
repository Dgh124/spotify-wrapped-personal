from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from.models import Feedback

from spotify_wrapped.Spotify import get_auth_url, get_access_token, get_all_info, create_duo_wrapped, has_access, get_user
from spotify_wrapped.Spotify import Error
from spotify_wrapped.modelControllers import *


def slideshow(request):
    access_token = request.session.get("access_token", None)
    expire_time = request.session.get("expire_time", None)
    refresh_token = request.session.get("refresh_token", None)

    # If not logged in yet, show base home page
    if not has_access(access_token, expire_time, refresh_token):
        return HttpResponseRedirect(reverse('spotify_wrapped:login'))

    user_info = get_all_info(access_token, expire_time, refresh_token)


    if isinstance(user_info, Error):
        print("failed generating slideshow")
        return render(request, "spotify_wrapped/slideshow.html", {})

    return render(request, "spotify_wrapped/slideshow.html", {
        "user_info": user_info.value,
        # "slides": ["games"],
        "slides": ["cover", "mood", "AI_Query", 
                   "artists", "genres", "albums", 
                   "popularityScore", 
                   # "recommendations", 
                   "tracks", "games",]
    })
    # Adolfo: artists, personality, albums, mood, genres, pop score, recommended, reciept


def wrapped(request):
    wrap_id = request.GET.get("uuid", None)
    if wrap_id is None:
        return HttpResponseRedirect(reverse("spotify_wrapped:index"))

    wrap_model = get_wrap(wrap_id)
    if wrap_model is None:
        return HttpResponseRedirect(reverse("spotify_wrapped:index"))
    wrap_object = convert_wrap_model(wrap_model)

    return render(request, "spotify_wrapped/slideshow.html", {
        "user_info": wrap_object,
        "slides": ["cover", "mood", "AI_Query", 
                   "artists", "genres", "albums", 
                   "popularityScore", "tracks", "games",]
    })



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
    if not has_access(access_token, expire_time, refresh_token):
        return HttpResponseRedirect(reverse('spotify_wrapped:login'))

    user_result = get_user(access_token, expire_time, refresh_token)
    if isinstance(user_result, Error):
        return HttpResponseRedirect(reverse('spotify_wrapped:login'))
    user_id = user_result.value.id
    
    wraps = get_all_user_wraps(user_id)
    return render(request, "spotify_wrapped/profile.html", {
        "wraps": wraps
    })


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
    if not has_access(access_token, expire_time, refresh_token):
        return HttpResponseRedirect(reverse("spotify_wrapped:login"))

    #spotify.py wrap object
    wrap_object = get_all_info(access_token, expire_time, refresh_token)
    if isinstance(wrap_object, Error):
        print("wrap object failed to build:", wrap_object.reason)
        return HttpResponseRedirect(reverse("spotify_wrapped:index"))

    #models wrap model
    converted_obj = convert_wrap_object_to_wrap_model(wrap_object.value)
    converted_obj.save()
    wrap_id = converted_obj.id
    wrapped_url = f'{reverse("spotify_wrapped:wrapped")}?uuid={wrap_id}'
    return HttpResponseRedirect(wrapped_url)


def delete_wrap(request):
    uuid = request.GET.get("uuid", None)
    if uuid is None:
        return HttpResponseRedirect(reverse("spotify_wrapped:index"))

    # delete_wrap logic
    return HttpResponseRedirect(reverse("spotify_wrapped:index"))

def duo_wrap(request):
    wrap_id = request.GET.get("uuid", None)
    if wrap_id is None:
        return HttpResponseRedirect(reverse("spotify_wrapped:index"))

    access_token = request.session.get("access_token", None)
    expire_time = request.session.get("expire_time", None)
    refresh_token = request.session.get("refresh_token", None)

    # If not logged in yet, show base home page
    if not has_access(access_token, expire_time, refresh_token):
        return HttpResponseRedirect(reverse("spotify_wrapped:login"))

    wrap1_model = get_wrap(wrap_id)
    if wrap1_model is None:
        return HttpResponseRedirect(reverse("spotify_wrapped:index"))
    wrap1 = convert_wrap_model(wrap1_model)

    wrap2 = get_all_info(access_token, expire_time, refresh_token)
    if isinstance(wrap2, Error):
        return HttpResponseRedirect(reverse("spotify_wrapped:index"))

    #spotify.py wrap object
    duo_wrap = create_duo_wrapped(wrap1, wrap2.value)

    #models wrap model
    duo_wrap_model = convert_wrap_object_to_wrap_model(duo_wrap)
    duo_wrap_model.save()
    print("Duo Wrap Model Users:")
    print(duo_wrap_model.user.all())

    wrap_id = duo_wrap_model.id
    wrapped_url = f'{reverse("spotify_wrapped:wrapped")}?uuid={wrap_id}'
    return HttpResponseRedirect(wrapped_url)


def logout(request):
    request.session.pop('access_token', None)
    request.session.pop('refresh_token', None)
    request.session.pop('expire_time', None)
    return HttpResponseRedirect(reverse('spotify_wrapped:index'))

def delete_account(request):
    access_token = request.session.get("access_token", None)
    expire_time = request.session.get("expire_time", None)
    refresh_token = request.session.get("refresh_token", None)

    user = get_user(access_token=access_token, expires_at= expire_time, refresh_token= refresh_token)
    if isinstance(user, Error):
        return HttpResponseRedirect(reverse('spotify_wrapped:login'))
    user_id = user.value.id

    wraps = get_all_user_wraps(user_id)

    if wraps is None:
        return HttpResponseRedirect(reverse('spotify_wrapped:login'))

    wraps.delete()

    UserModel.objects.get(id=user_id).delete()
    return HttpResponseRedirect(reverse('spotify_wrapped:logout'))

def delete_wrap(request):
    wrap_id = request.GET.get("uuid", None)
    if wrap_id is None:
        return HttpResponseRedirect(reverse("spotify_wrapped:index"))

    wrap_model = get_wrap(wrap_id)
    if wrap_model is None:
        return HttpResponseRedirect(reverse("spotify_wrapped:index"))


    wrap_model.delete()
    return HttpResponseRedirect(reverse("spotify_wrapped:index"))
