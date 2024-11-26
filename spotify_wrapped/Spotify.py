import base64
import os, requests, time
import urllib.parse
from typing import Callable
from openai import OpenAI
import json

from dotenv import load_dotenv
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
chatgpt = os.getenv("CHATGPT_KEY")

class Artist:
    def __init__(self, name:str, _id:str, image:str, genres:str):
        self.name = name
        self.id = _id
        self.image = image
        self.genres = genres

class Track:
    def __init__(self, _id:str, album_name:str, album_image:str, song_name:str, artists:list[str], preview_url:str|None, popularity_score:int):
        """
        Initializes Track object
        :param id: Unique spotify id of the track
        :param album_name: Name of the album the track was released in
        :param album_image: URL of the smallest image corresponding to the album
        :param song_name: Track name
        :param artists: List of the names of artists on the track
        :param preview_url: Link to a 30s preview of the track
        :param popularity_score: 
        """
        self.id = _id
        self.album_name = album_name
        self.album_image = album_image
        self.name = song_name
        self.artists = artists
        self.preview_url = preview_url
        self.popularity_score = popularity_score

class User:
    def __init__(self, display_name:str, _id:str, pfp:str, product:str, uri:str):
        self.display_name = display_name
        self.id = _id
        self.pfp = pfp
        self.product = product
        self.uri = uri

class WrapObject:
    def __init__(self, top_tracks:list[Track], top_artists:list[Artist], user:User, suggested_tracks:list[Track], personality:list[str], color):
        self.top_tracks = top_tracks
        self.top_artists = top_artists
        self.top_albums = get_top_albums(top_tracks)
        self.user = user
        self.top_genres = get_top_genres(top_artists)
        self.audio_link = get_top_track_audio_link(top_tracks)
        self.suggested_tracks = suggested_tracks
        self.personality = personality
        self.color = color

redirect_uri = "http://127.0.0.1:8000/auth"


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
    """
    queries Spotify api using access token
    :param url: url to query
    :param access_token: access token returned by Spotify api callback at /auth path
    :return: returns response.json() if successful; returns None otherwise
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        print(f"Client not authorized to make request at {url}")
    else:
        print(f"{url} request returned error code {response.status_code}")
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


def get_user_attributes[T](access_token: str, expires_at: int, refresh_token: str, url_slug: str, output_transform: Callable[[dict], T]) -> dict[str, str|T]:
    """
    Queries the Spotify api for a user's top artists
    :param access_token: access token returned by spotify API callback at /auth path
    :param expires_at: expires_at time returned by spotify API callback at /auth path
    :param refresh_token: refresh token returned by spotify API callback at /auth path
    :param url_slug: url path to append onto api.spotify.com/v1/me/{url_slug}
    :param output_transform: function to transform output of get_requests to usable format
    :return: dict of form {status: success|error} and a value if success, reason if failure
    """
    if not has_access(access_token, expires_at, refresh_token):
        return {"status":"error", "reason":"noToken"}

    url = f"https://api.spotify.com/v1/me/{url_slug}"
    response = get_requests(url, access_token)

    if response is None:
        return {"status":"error", "reason":"request failure"}

    value = output_transform(response)
    return {"status":"success", "value":value}


def get_user(access_token, expires_at, refresh_token):
    """
    queries spotify API for user attributes
    :param access_token:
    :param expires_at:
    :param refresh_token:
    :return:
    """
    user_transform_fn = lambda response : User(
        display_name = response.get("display_name", None),
        _id= response.get("id", None),
        pfp = response.get('images') and response['images'][0].get('url') if response['images'] else None,
        product = response.get("product", None),
        uri = response.get("uri", None),
    )
    return get_user_attributes(access_token, expires_at, refresh_token,
                               "", user_transform_fn)


def get_top_tracks(access_token, expires_at, refresh_token, time_range='medium_term', limit=10):
    """
    Queries Spotify API for user's top tracks over a time range
    :param access_token: see get_user_attributes
    :param expires_at: see get_user_attributes
    :param refresh_token: see get_user_attributes
    :param time_range: over what time the top tracks are computed (short_term, medium_term, long_term)
    :param limit: how many top tracks to return (between 1-50)
    :return: list of Track items including details about the top tracks
    """
    top_track_transform_fn = lambda response : [
        Track(
            _id=track["id"],
            album_name=track["album"]["name"],
            album_image=track["album"]["images"][0]["url"] if track["album"]["images"] else "",
            song_name=track["name"],
            artists=[artist["name"] for artist in track["artists"]],
            preview_url=track.get("preview_url", ""),
            popularity_score=track["popularity"]
        )
        for track in response["items"]
    ]
    limit = min(max(1, limit), 50)
    return get_user_attributes(access_token, expires_at, refresh_token,
                               f"top/tracks?time_range={time_range}&limit={limit}",
                               top_track_transform_fn)


def get_top_artists(access_token, expires_at, refresh_token, time_range="medium_term", limit=10):
    """
    Queries the Spotify api for a user's top artists
    :param access_token: see get_user_attributes
    :param expires_at: see get_user_attributes
    :param refresh_token: see get_user_attributes
    :param time_range: over what time the top artists are computed (short_term, medium_term, long_term)
    :param limit: how many top artists to return (between 1-50)
    :return: list of Artist items including details about the top artists
    """
    top_artists_transform_fn = lambda response : [
        Artist(
            name=artist["name"],
            _id=artist["id"],
            image=artist["images"][0]["url"] if artist["images"] else "",
            genres=artist["genres"],
        ) for artist in response["items"]
    ]
    limit = min(max(1, limit), 50)
    return get_user_attributes(
        access_token, expires_at, refresh_token,
        f"top/artists?time_range={time_range}&limit={limit}", top_artists_transform_fn
    )


def get_top_genres(top_artists: list[Artist]) -> list[tuple[str,int]]:
    """
    returns top genres given a list of artists
    :param top_artists: sorted list of user's top artists
    :return: the top {count} genres that a user enjoys
    """
    top_genres = {}
    for artist in top_artists:
        for genre in artist.genres:
            if genre in top_genres:
                top_genres[genre] += 1
            else:
                top_genres[genre] = 1
    return [
        (genre[0], genre[1]) for genre in
        sorted(top_genres.items(), key=lambda item: item[1], reverse=True)
    ]


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


def get_top_albums(top_tracks: list[Track]) -> list[tuple[str, list[Track]]]:
    albums = {}
    for track in top_tracks:
        if track.album_name in albums:
            albums[track.album_name].append(track)
        else:
            albums[track.album_name] = [track]
    return sorted(albums.items(), key=lambda item: len(item[1]), reverse=True)


def get_suggested_tracks(access_token, top_artists: list[Artist]=[]) -> dict[str,list[Track]|str]:
    """
    queries spotify API for suggested tracks based on list of artists
    :param access_token: see get_user_attributes
    :param top_artists: sorted list of user's top artists'
    :return: list of suggested tracks
    """
    # gets the top five artists for a user
    count = 0
    artist_seeds = ""
    while count < len(top_artists) and count < 5:
        artist_seeds += top_artists[count].id + ','
        count += 1

    url = f'https://api.spotify.com/v1/recommendations?seed_artists={artist_seeds}'
    response = get_requests(url, access_token)
    if response is None:
        return {"status": "error", "reason": "suggested tracks returned error status code"}
    return {"status": "success", "value": [
        Track(
            _id=track["id"],
            album_name=track["album"]["name"],
            album_image=track["album"]["images"][-1]["url"] if track["album"]["images"] else "",
            song_name=track["name"],
            artists=[artist["name"] for artist in track["artists"]],
            preview_url=track.get("preview_url", ""),
            popularity_score=track["popularity"],
        )
        for track in response["tracks"]
    ]}


def get_personality_and_colors(artists: list):
    client = OpenAI(
        api_key=chatgpt,
    )

    artist_list = ""
    for artist in artists:
        artist_list += f"{artist}, "

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f""" what insight can you give about my personality if i listen to 
                                {artist_list}. 
                                simplify the answer in bullet points with only the keyword. 
                                Make sure the keyword are tied to words that typically used to describe personality.
                                Also generate 5 hex code based on the personalities.
                                Return in the format 
                                "personality1 personality2 personality3 personality4 personality5 Hex1 Hex2 Hex3 Hex4 Hex5" 
                                Dont not include any heading! NO COMMAS! """
            }
        ],
        model="gpt-3.5-turbo",
    )
    response = chat_completion.choices[0].message.content
    res_list = response.split()
    personality = res_list[:5]
    personality_color = res_list[5:]
    return personality, personality_color


def get_all_info(access_token, expires_at, refresh_token) -> dict[str, str | WrapObject]:
    top_tracks_result = get_top_tracks(
        access_token=access_token, expires_at=expires_at, refresh_token=refresh_token, limit=50
    )
    user_result = get_user(
        access_token=access_token, expires_at=expires_at, refresh_token=refresh_token,
    )
    top_artists_result = get_top_artists(
        access_token=access_token, expires_at=expires_at, refresh_token=refresh_token,
    )
    if top_tracks_result["status"] == "error" or top_artists_result["status"] == "error" or top_tracks_result["status"] == "error":
        return {"status": "error", "reason": "request returned error status code"}

    suggested_tracks = get_suggested_tracks(
        access_token=access_token,
        top_artists=top_artists_result["value"],
    )
    if suggested_tracks["status"] == "error":
        return suggested_tracks #includes error message and value

    personality, color = get_personality_and_colors(top_artists_result['value'])

    return {"status": "success", "value": WrapObject(
        top_tracks=top_tracks_result["value"],
        top_artists=top_artists_result["value"],
        user=user_result["value"],
        suggested_tracks=suggested_tracks["value"],
        personality=personality,
        color = json.dumps(color)
    )}



