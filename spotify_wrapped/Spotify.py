import base64
import os, requests, time
import urllib.parse

from dotenv import load_dotenv, dotenv_values

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


load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
auth_code = None
access_token = None
refresh_token = None
expires_at = 0
# data = {
#     "grant_type" : "authorization_code",
#     "client_id" : client_id,
#     "client_secret" : client_secret,
#     'code' : auth_code,
#     'redirect_uri': redirect_uri
# }
redirect_uri = "https://localhost:8000"
headers = {
    "Authorization": f"Bearer {access_token}"
}

def get_auth_url():
    redirect_url = 'https://localhost:8000'
    # Define the scope you need (e.g., user-read-private)
    scope = 'user-read-private user-read-email user-top-read'

    # Construct the authorization URL
    auth_url = 'https://accounts.spotify.com/authorize'
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_url,
        'scope': scope
    }

    full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return full_auth_url

def get_requests(url):
    response = requests.get(url, headers=headers)
    user_json = response.json()
    return user_json

def is_token_expired():
    current_time = time.time()
    return current_time >= expires_at

def get_access_token():
    token_url = "https://accounts.spotify.com/api/token"
    data_t = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        'code': auth_code,
        'redirect_uri': redirect_uri
    }
    token_headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    token_response = requests.post(token_url, data=data_t, headers=token_headers)
    token_json_response = token_response.json()
    access_token1= token_json_response.get("access_token")
    refresh_token1 = token_json_response.get("refresh_token")
    print("Access_token", access_token1)
    print("Refresh_token", refresh_token1)

def refresh_access_token():
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        'Authorization': f'Basic {client_creds_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    response = requests.post(token_url, headers=headers, data=data)
    token = response.json()
    expires_in = token.get('expires_in', 3600)
    expires_at = time.time() + expires_in
    access_token = token.get('access_token')

def get_top_artist():
    if access_token is None and refresh_token is None:
        get_access_token()
    if is_token_expired():
        refresh_access_token()
    url = "https://api.spotify.com/v1/me/top/artists?time_range=long_term&limit=10"
    response = get_requests(url)
    top_artists = []
    for item in response["items"]:
        artist = Artist(item['name'], item['id'], item['images'][0]['url'], item['genres'])
        top_artists.append(artist)
    return top_artists

def get_top_track():
    if access_token is None and refresh_token is None:
        get_access_token()
    if is_token_expired():
        refresh_access_token()
    url = "https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=10"
    response = get_requests(url)
    print(response)
    top_tracks = []
    for item in response['items']:
        track = Track(item['album']['name'], item['album'][0]['url'], item['name'])
        top_tracks.append(track)
    return top_tracks

# print(get_auth_url())
# print(get_access_token())

for artist in get_top_artist():
    print(artist.name)