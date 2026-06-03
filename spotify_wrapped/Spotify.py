import base64
import os, requests, time
import urllib.parse
from typing import Callable, Literal, Union
import json
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv("CLIENT_ID") or os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET") or os.getenv("SPOTIFY_CLIENT_SECRET")
github_models_token = os.getenv("GITHUB_MODELS_TOKEN") or os.getenv("GITHUB_TOKEN") or os.getenv("CHATGPT_KEY")
github_models_model = os.getenv("GITHUB_MODELS_MODEL", "openai/gpt-5")
github_models_endpoint = os.getenv(
    "GITHUB_MODELS_ENDPOINT",
    "https://models.github.ai/inference/chat/completions",
)

class Success[T]:
    def __init__(self, value:T):
        self.status = Literal["success"]
        self.value = value
class Error:
    def __init__(self, reason:str):
        self.status = Literal["error"]
        self.reason = reason

class Artist:
    def __init__(self, name:str, _id:str, image:str, genres:list[str]):
        self.name = name
        self.id = _id
        self.image = image
        self.genres = genres
    def __str__(self):
        return self.name

class Track:
    def __init__(self, _id:str, album_name:str, album_image:str, song_name:str, artists:list[str], preview_url:str|None, popularity_score:int):
        """
        Initializes Track object
        :param _id: Unique spotify id of the track
        :param album_name: Name of the album the track was released in
        :param album_image: URL of the smallest image corresponding to the album
        :param song_name: Track name
        :param artists: List of the names of artists on the track
        :param preview_url: Link to a 30s preview of the track
        :param popularity_score: 
        """
        self._id = _id
        self.album_name = album_name
        self.album_image = album_image
        self.song_name = song_name
        self.artists = artists
        self.preview_url = preview_url
        self.popularity_score = popularity_score

    def __str__(self):
        return self.song_name

    @property
    def id(self):
        return self._id


class User:
    def __init__(self, display_name:str, _id:str, pfp:str, product:str, uri:str):
        self.display_name = display_name
        self.id = _id
        self.pfp = pfp
        self.product = product
        self.uri = uri


    def __str__(self):
        return self.id

    def get_user_id(self):
        return self.id

class WrapObject:
    def __init__(self, top_tracks:list[Track], top_artists:list[Artist], users:list[User], suggested_tracks: list[Track], personality:list[str], color):
        self.top_tracks = top_tracks
        self.top_artists = top_artists
        self.top_albums = get_top_albums(top_tracks)
        self.users = users
        self.top_genres = get_top_genres(top_artists)
        self.audio_link = get_top_track_audio_link(top_tracks)
        self.suggested_tracks = suggested_tracks
        self.personality = personality
        self.color = color

    def __str__(self):
        return (f"Top Tracks:{self.top_tracks}\n"
                f"Top Artists:{self.top_artists}\n"
                f"User: {self.users}\n"
                f"Top Genres: {self.top_genres}\n"
                f"Audio Link: {self.audio_link}\n"
                f"Suggested Tracks: {self.suggested_tracks}\n"
                f"Personality: {self.personality}\n"
                f"Color: {self.color}\n")

redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8000/auth/")


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


def get_access_token(auth_code:str) -> tuple[str, int, str] | Error:
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
    token_response = res.json()

    access_token:str = token_response.get("access_token")
    expires_in: int = token_response.get("expires_in")
    refresh_token:str = token_response.get("refresh_token")
    if not access_token or not expires_in or not refresh_token:
        reason = token_response.get("error_description") or token_response.get("error") or "token request failed"
        return Error(reason)

    expire_time: int = int(time.time()) + expires_in
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
    new_refresh_token:str = json.get('refresh_token')

    return access_token, expires_at, new_refresh_token


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
        print(dir(response))
        print(f"Client not authorized to make request at {url}")
    else:
        print(f"{url} request returned error code {response.status_code}")
    return None


def is_token_expired(expires_at:int) -> bool:
    current_time = time.time()
    return current_time >= expires_at


def has_access(access_token:str|None, expires_at:int|None, refresh_token:str|None):
    if access_token is None or refresh_token is None or expires_at is None:
        return False
    if is_token_expired(expires_at):
        refresh_access_token(refresh_token)
    return True


def get_user_attributes[T](access_token: str, expires_at: int, refresh_token: str, url_slug: str, output_transform: Callable[[dict], T]) -> Union[Success[T], Error]:
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
        return Error("noToken")

    url = f"https://api.spotify.com/v1/me/{url_slug}"
    response = get_requests(url, access_token)

    if response is None:
        return Error("request failure")

    value = output_transform(response)
    return Success(value)


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
        pfp = response.get('images') and response['images'][0].get('url') if response['images'] else "",
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


def get_suggested_tracks(access_token, top_artists: list[Artist]=[]) -> Union[Success[list[Track]], Error]:
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
        return Error("suggested tracks returned error status code")
    return Success([
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
    ])


def get_personality_and_colors(artists: list[Artist]):
    artist_list = "".join(str(artist)+"," for artist in artists)

    if not github_models_token:
        print("GitHub Models token is not configured")
        return [""], ""

    prompt = f""" what insight can you give about my personality if i listen to
                                {artist_list}.
                                simplify the answer in bullet points with only the keyword.
                                Make sure the keyword are tied to words that typically used to describe personality.
                                Also generate 5 hex code based on the personalities.
                                Return in the format
                                "personality1 personality2 personality3 personality4 personality5 Hex1 Hex2 Hex3 Hex4 Hex5"
                                Dont not include any heading! NO COMMAS! """
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_models_token}",
        "X-GitHub-Api-Version": "2026-03-10",
        "Content-Type": "application/json",
    }
    payload = {
        "model": github_models_model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 100,
    }

    try:
        model_response = requests.post(
            github_models_endpoint,
            headers=headers,
            json=payload,
            timeout=30,
        )
        if model_response.status_code != 200:
            print("GitHub Models request failed:", model_response.status_code, model_response.text[:300])
            return [""], ""
        response = model_response.json()["choices"][0]["message"].get("content")
    except (KeyError, IndexError, requests.RequestException, ValueError) as err:
        print("GitHub Models request failed:", err)
        return [""], ""

    if response is None:
        return [""], ""
    print(response)
    res_list = response.replace(',', ' ').split()
    personality = [word.lower() for word in res_list[:5]]
    personality_color = res_list[5:]
    return personality, personality_color


def get_all_info(access_token, expires_at, refresh_token, time_range="medium_term") -> Union[Success[WrapObject], Error]:
    top_tracks_result = get_top_tracks(
        access_token=access_token, expires_at=expires_at, refresh_token=refresh_token, 
        time_range=time_range, limit=50
    )
    user_result = get_user(
        access_token=access_token, expires_at=expires_at, refresh_token=refresh_token,
    )
    top_artists_result = get_top_artists(
        access_token=access_token, expires_at=expires_at, refresh_token=refresh_token, 
        time_range=time_range,
    )
    if isinstance(top_tracks_result, Error) or isinstance(user_result, Error) or isinstance(top_artists_result, Error):
        return Error("request returned error status code")

    # suggested_tracks = get_suggested_tracks(
    #     access_token=access_token,
    #     top_artists=top_artists_result.value,
    # )
    # if isinstance(suggested_tracks, Error):
    #     return suggested_tracks #includes error message and value
    suggested_tracks = Success([])

    personality, color = get_personality_and_colors(top_artists_result.value)

    return Success(WrapObject(
        top_tracks=top_tracks_result.value,
        top_artists=top_artists_result.value,
        users=[user_result.value],
        suggested_tracks=suggested_tracks.value,
        personality=personality,
        color = json.dumps(color)
    ))

# 1. Get user1's (senders) wrap model -> wrap obj
# 2. Create user2's wrap obj with get_all_info
# 3. Merge artists, tracks, genres
# 4. Make merged wrap obj -> convert to wrap model
# 5. Make duoWrap model instance that holds both user wrap id's

# Note: no need to merge top_genres, this will come from the merged
# top artists.
def union[T](arr1:list[T], arr2:list[T])->list[T]:
    outArr = []
    arr2_str = [str(elem) for elem in arr2]
    for elem in arr1:
        if str(elem) in arr2_str:
            outArr.append(elem)
    return outArr

def merge[T](arr1:list[T], arr2:list[T], count:int)->list[T]:
    shared = union(arr1, arr2)
    str_shared = [str(elem) for elem in shared]
    i = j = 0
    while len(shared) < count:
        if i < j and i < len(arr1):
            if str(arr1[i]) not in str_shared:
                shared.append(arr1[i])
            i += 1
        elif j <= i and j < len(arr2):
            if str(arr2[j]) not in str_shared:
                shared.append(arr2[j])
            j += 1
        else:
            return shared
    return shared


def create_duo_wrapped(wrap1:WrapObject, wrap2:WrapObject)->WrapObject:
    # if wrap1.user.id == wrap2.user.id:
    #     return None
    # Ensure we don't iterate out of bounds for anything
    num_merge = 10

    merged_artists = merge(wrap1.top_artists, wrap2.top_artists, num_merge)
    merged_tracks = merge(wrap1.top_tracks, wrap2.top_tracks, num_merge)

    personality, color = get_personality_and_colors(merged_artists)

    print("Duo Wrapped Users:")
    print((wrap1.users + wrap2.users))
    return WrapObject(
                top_tracks=merged_tracks,
                top_artists=merged_artists,
                users=(wrap1.users + wrap2.users),
                suggested_tracks=[],
                personality=personality,
                color=json.dumps(color)
            )
