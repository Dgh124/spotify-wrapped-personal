import base64
import os, requests, time
import urllib.parse

from dotenv import load_dotenv, dotenv_values

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

class Spotify:
    def __init__(self):
        self.expires_at = 0
        self.access_token = None
        self.auth_code = None
        self.refresh_token = None
        self.redirect_uri = 'https://localhost:8000'
        self.data = {
            "grant_type" : "authorization_code",
            "client_id" : client_id,
            "client_secret" : client_secret,
            'code' : self.auth_code,
            'redirect_uri': self.redirect_uri
        }
        self.redirect_uri = "https://localhost:8000"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

    #Set auth code after signing in
    def set_auth_code(self, code):
        self.auth_code = code

    #URL needed to sign in and get auth code
    def get_auth_url(self):
        # Define the scope you need (e.g., user-read-private)
        scope = 'user-read-private user-read-email user-top-read'

        # Construct the authorization URL
        auth_url = 'https://accounts.spotify.com/authorize'
        params = {
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': scope
        }

        full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
        return full_auth_url


    def get_requests(self, url):
        response = requests.get(url, headers=self.headers)
        user_json = response.json()
        return user_json

    def is_token_expired(self):
        current_time = time.time()
        return current_time >= self.expires_at

    def get_access_token(self):
        token_url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            'code': self.auth_code,
            'redirect_uri': self.redirect_uri
        }
        token_headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        token_response = requests.post(token_url, data=data, headers=token_headers)
        token_json_response = token_response.json()
        self.access_token = token_json_response.get("access_token")
        self.refresh_token = token_json_response.get("refresh_token")

    def refresh_access_token(self):
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
        token_url = "https://accounts.spotify.com/api/token"
        headers = {
            'Authorization': f'Basic {client_creds_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        response = requests.post(token_url, headers=headers, data=data)
        token = response.json()
        expires_in = token.get('expires_in', 3600)
        self.expires_at = time.time() + expires_in
        self.access_token = token.get('access_token')

    def get_top_artist(self):
        if self.access_token is None and self.refresh_token is None:
            self.get_access_token()
        if self.is_token_expired():
            self.refresh_access_token()
        url = "https://api.spotify.com/v1/me/top/artists?time_range=long_term&limit=10"
        response = self.get_requests(url)
        top_artists = []
        for item in response["items"]:
            artist = Artist(item['name'], item['id'], item['images'][0]['url'], item['genres'])
            top_artists.append(artist)
        return top_artists

    def get_top_track(self):
        if self.is_token_expired():
            self.refresh_access_token()
        url = "https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=10"
        response =self.get_requests(url)
        top_tracks = []
        for item in response['items']:
            track = Track(item['album']['name'], item['album'][0]['url'], item['name'])
            top_tracks.append(track)