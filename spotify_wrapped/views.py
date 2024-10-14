from django.shortcuts import render

def index(request):
    return render(request, "spotify_wrapped/home.html", {})