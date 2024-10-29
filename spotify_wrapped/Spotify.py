import base64
import os, requests, time
import urllib.parse
from typing import TypedDict

from dotenv import load_dotenv
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

class Artist:
    def __init__(self, name:str, id:str, image:str, genres:str):
        self.name = name
        self.id = id
        self.image = image
        self.genres = genres

class Track:
    def __init__(self, album_name:str, album_image:str, song_name:str, artists:list[str], preview_url:str|None):
        """
        Initializes Track object
        :param album_name: Name of the album the track was released in
        :param album_image: URL of the smallest image corresponding to the album
        :param song_name: Track name
        :param artists: List of the names of artists on the track
        :param preview_url: Link to a 30s preview of the track
        """
        self.album_name = album_name
        self.album_image = album_image
        self.name = song_name
        self.artists = artists
        self.preview_url = preview_url

class User:
    def __init__(self, display_name:str, _id:str, pfp:str, product:str, uri:str):
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
        'scope': scope,
        'show_dialog': "true"
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
        'redirect_uri': redirect_uri,
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
    if response.status_code == 200:
        return response.json()
    else:
        return None


def is_token_expired(expires_at:int) -> bool:
    current_time = time.time()
    return current_time >= expires_at


def has_access(access_token:str, expires_at:int, refresh_token:str):
    if access_token is None and refresh_token is None:
        return False
    if is_token_expired(expires_at):
        refresh_access_token(refresh_token)

    return True


def get_user_attributes(access_token, expires_at, refresh_token, url_slug, output_transform):
    if not has_access(access_token, expires_at, refresh_token):
        return {"status":"error", "reason":"noToken"}

    url = f"https://api.spotify.com/v1/me/{url_slug}"
    response = get_requests(url, access_token)

    if response is None:
        return {"status":"error", "reason":"request failure"}

    value = output_transform(response)
    return {"status":"success", "value":value}


def get_user(access_token, expires_at, refresh_token):
    user_transform_fn = lambda response : User(
        display_name = response.get("display_name", None),
        _id= response.get("id", None),
        pfp = response.get('images') and response['images'][0].get('url') if response['images'] else None,
        product = response.get("product", None),
        uri = response.get("uri", None),
    )
    return get_user_attributes(access_token, expires_at, refresh_token,
                               "", user_transform_fn)


'''Added time_range option that simply appends a specific time_range to the API url'''
def get_top_tracks(access_token, expires_at, refresh_token, time_range='long_term'):
    top_track_transform_fn = lambda response : [
        Track(
            album_name=track["album"]["name"],
            album_image=track["album"]["images"][-1]["url"] if track["album"]["images"] else "",
            song_name=track["name"],
            artists=[artist["name"] for artist in track["artists"]],
            preview_url=track["preview_url"]
        )
        for track in response["items"]
    ]
    return get_user_attributes(access_token, expires_at, refresh_token,
                               f"top/tracks?time_range={time_range}", top_track_transform_fn)


'''This function takes in an access_token, expires_at time, and refresh token. It first calls get
user attributes to ensure the access key is valid, and a valid response is returned. 
It then applies a transformation function that takes in a response and creates both a list
of Artist() and top genres from that response. The Artist() list and top genre list
are returned as a tuple.'''
def get_top_artists(access_token, expires_at, refresh_token):
    top_genres = {}

    def add_genre(arr, genre):
        if genre in arr:
            arr[genre] += 1
        else:
            arr[genre] = 1

    def sort_genres(arr):
        return sorted(arr.items(), key=lambda item: item[1], reverse=True)

    def transform_top_artists(response):
        artists = []
        for artist_data in response["items"]:
            artist = Artist(
                name=artist_data["name"],
                id=artist_data["id"],
                image=artist_data["images"][-1]["url"] if artist_data["images"] else "",
                genres=artist_data["genres"],
            )
            artists.append(artist)
            for genre in artist.genres:
                add_genre(top_genres, genre)
        return artists

    # Use get_user_attributes to make the request
    top_artists_result = get_user_attributes(
        access_token, expires_at, refresh_token,
        "top/artists", transform_top_artists
    )

    # Check if the API call was successful
    if top_artists_result['status'] == 'success':
        top_artists = top_artists_result['value']
        top_genres_sorted = sort_genres(top_genres)
        return ({"status": "success", "value": top_artists}, top_genres_sorted)
    else:
        return ({"status": "error", "reason": top_artists_result['reason']}, [])





def get_top_track_audio_link(track_list: list[Track]) -> str:
    """
    Returns link of highest-rated song with preview url
    :param track_list: list of Tracks sorted in order of preference
    :return: link to highest-rated song preview mp3
    """
    for track in track_list:
        if track.preview_url is not None:
            return track.preview_url
    return ""

def get_suggested_genres(access_token):
    url = 'https://api.spotify.com/v1/recommendations/available-genre-seeds'
    response = get_requests(url, access_token)
    # print(response)
    genres = []
    for genre in response["genres"]:
        genres.append(genre)
    # print(genres)
    return genres


