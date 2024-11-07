import base64
import os, requests, time
import urllib.parse
from typing import TypedDict

from dotenv import load_dotenv
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

class Artist:
    def __init__(self, name, id,  image, genre):
        self.name = name
        self.id = id
        self.image = image
        self.genre = genre
class Track:
    def __init__(self, album_name, album_image, song_name):
        self.album_name = album_name
        self.album_image = album_image
        self.song_name = song_name

class User:
    def __init__(self, display_name, _id, pfp, product, uri):
        self.display_name = display_name
        self.id = _id
        self.pfp = pfp
        self.product = product
        self.uri = uri

redirect_uri = "http://localhost:8000/auth"


def get_auth_url():
    # Construct the authorization URL
    auth_url = 'https://accounts.spotify.com/authorize'

    # Gives access to user profile and top tracks, albums, etc.
    scope = 'user-read-private user-read-email user-top-read'
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scope
    }

    full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return full_auth_url


def get_access_token(auth_code:str) -> (str, int, str):
    """
    Takes auth_code and returns Spotify api access token
    :param auth_code: auth code returned by get_auth_url called at /login slug
    :return: (access_token, expire_time, refresh_token)
    """
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        'code': auth_code,
        'redirect_uri': redirect_uri
    }
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
    headers = {
        "Authorization": f"Basic {client_creds_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    res = requests.post(url, data=data, headers=headers)
    json = res.json()

    access_token:str = json.get("access_token")
    expires_in: int = json["expires_in"]
    expire_time: int = int(time.time()) + expires_in
    refresh_token:str = json.get("refresh_token")

    return access_token, expire_time, refresh_token


def refresh_access_token(refresh_token:str):
    token_url = "https://accounts.spotify.com/api/token"
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
    headers = {
        'Authorization': f'Basic {client_creds_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    response = requests.post(token_url, headers=headers, data=data)
    json = response.json()

    access_token:str = json.get('access_token')
    expires_in = json.get('expires_in', 3600)
    expires_at = int(time.time()) + expires_in
    refresh_token:str = json.get('refresh_token')

    return access_token, expires_at, refresh_token


def get_requests(url, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    json = response.json()
    return json


def is_token_expired(expires_at:int) -> bool:
    current_time = time.time()
    return current_time >= expires_at


def has_access(access_token:str, expires_at:int, refresh_token:str):
    if access_token is None and refresh_token is None:
        return False
    if is_token_expired(expires_at):
        refresh_access_token(refresh_token)

    return True


def get_top_artists(access_token, expires_at, refresh_token,):
    if not has_access(access_token, expires_at, refresh_token):
        return {"status":"error", "reason":"noToken"}

    url = f"https://api.spotify.com/v1/me/top/artists?time_range=long_term"
    response = get_requests(url, access_token)

    top_artists = [
        Artist(item['name'], item['id'], item['images'][0]['url'], item['genres'])
        for item in response["items"]
    ]
    return {"status":"success", "value":top_artists}


def get_top_tracks(access_token, expires_at, refresh_token,):
    if not has_access(access_token, expires_at, refresh_token):
        return {"status":"error", "reason":"noToken"}

    url = f"https://api.spotify.com/v1/me/top/tracks?time_range=long_term"
    response = get_requests(url, access_token)

    top_tracks = []
    for item in response["items"]:
        top_tracks.append(
            Track(item['album']['name'], item['album']['images'][0]['url'], item['name'])
        )

    return {"status":"success", "value":top_tracks}

def get_user(access_token, expires_at, refresh_token):
    """
    Gets user details from Spotify API and returns User object with attributes
    :param access_token:
    :param expires_at:
    :param refresh_token:
    :return: display_name, uid, pfp, product, uri
    """
    if not has_access(access_token, expires_at, refresh_token):
        return {"status":"error", "reason":"noToken"}

    url = "https://api.spotify.com/v1/me"
    response = get_requests(url, access_token)

    user = User(
        display_name = response.get("display_name", None),
        _id= response.get("id", None),
        pfp = response.get('images') and response['images'][0].get('url') if response['images'] else None,
        product = response.get("product", None),
        uri = response.get("uri", None),
    )
    return {"status":"success", "value":user}

