from spotify_wrapped.Spotify import Track, WrapObject, Artist, User
from spotify_wrapped.models import TrackModel, ArtistModel, WrapModel, UserModel

def convert_tuple_to_dict(tuple_list):
    return {key:value for (key,value) in tuple_list}

def convert_dict_to_tuple(dictionary):
    return list(tuple(dictionary.items()))

def convert_track_object_to_track_model(track_obj):
    #print(track_obj.__str__())
    track_id = track_obj.id
    album_name = track_obj.album_name
    album_image = track_obj.album_image
    name = track_obj.song_name
    artists = track_obj.artists
    preview_url = track_obj.preview_url
    popularity_score = track_obj.popularity_score
    new_track = TrackModel(track_id = track_id, album_name=album_name, album_image=album_image, track_name=name, artist_list=artists,
                      preview_url=preview_url, popularity_score=popularity_score)
    new_track.save()
    return new_track


def convert_artist_object_to_artist_model(artist_obj):
    name = artist_obj.name
    image = artist_obj.image
    artist_id = artist_obj.id
    genres = artist_obj.genres
    new_artist = ArtistModel(id = artist_id, name = name, image = image, genres = genres)
    new_artist.save()
    return new_artist

def convert_user_object_to_user_model(user_obj):
    display_name = user_obj.display_name
    user_id = user_obj.id
    pfp = user_obj.pfp
    product = user_obj.product
    uri = user_obj.uri
    new_user = UserModel(display_name = display_name, id = user_id, product = product, uri = uri, pfp = pfp)
    new_user.save()
    return new_user

def convert_wrap_object_to_wrap_model(wrap_obj):
    top_tracks = [convert_track_object_to_track_model(track) for track in wrap_obj['value'].top_tracks]
    top_artists = [convert_artist_object_to_artist_model(artist) for artist in wrap_obj['value'].top_artists]
    user = convert_user_object_to_user_model(wrap_obj['value'].user)
    suggested_tracks = [convert_track_object_to_track_model(track) for track in wrap_obj['value'].suggested_tracks]
    personality = wrap_obj['value'].personality
    top_audio = wrap_obj['value'].audio_link
    color = wrap_obj['value'].color
    top_genres = convert_tuple_to_dict(wrap_obj['value'].top_genres)
    #need to add them using manytomany .add()
    new_wrap = WrapModel(color = color, personality = personality,
                    top_audio = top_audio, top_genres=top_genres)
    new_wrap.save()
    new_wrap.top_tracks.add(*top_tracks)
    new_wrap.top_artists.add(*top_artists)
    new_wrap.suggested_tracks.add(*suggested_tracks)
    new_wrap.user.add(user)
    return new_wrap

def get_wrap(wrap_id):
    return WrapModel.objects.get(id = wrap_id)

#user id is the id they have on spotify. saved on both
def get_all_user_wraps(user_id):
    user = UserModel.objects.get(id = user_id)
    return user.user.all()



def convert_track_model(track_model):
    track_album_name = track_model.album_name
    track_album_image = track_model.album_image
    track_name = track_model.track_name
    track_id = track_model.id
    track_artists = track_model.artist_list
    track_preview_url = track_model.preview_url
    track_popularity_score = track_model.popularity_score
    new_track = Track(album_name=track_album_name, album_image=track_album_image, preview_url=track_preview_url,
                      song_name= track_name, artists=track_artists,_id = track_id, popularity_score=track_popularity_score)
    return new_track


def convert_artist_model(artist_model):
    artist_name = artist_model.name
    artist_id = artist_model.id
    artist_genres = artist_model.genres
    artist_image = artist_model.image
    new_artist = Artist(name=artist_name, image=artist_image, genres=artist_genres, _id=artist_id)
    return new_artist


def convert_user_model(user_model):
    user_id = user_model.id
    user_display_name = user_model.display_name
    user_pfp = user_model.pfp
    user_product = user_model.product
    user_uri = user_model.uri
    new_user = User(_id = user_id,display_name=user_display_name, pfp=user_pfp,
                    product=user_product, uri=user_uri )
    return new_user


def convert_wrap_model(wrap_model):
    wrap_user = convert_user_model(wrap_model.user.first())
    top_tracks = [convert_track_model(track) for track in wrap_model.top_tracks.all()]
    top_artists = [convert_artist_model(artist) for artist in wrap_model.top_artists.all()]

    #top_genres = convert_dict_to_tuple(wrap_model.top_genres)
    #audio_link = wrap_model.top_audio
    suggested_tracks = [convert_track_model(track) for track in wrap_model.suggested_tracks.all()]
    personality = wrap_model.personality
    color = wrap_model.color
    new_wrap = WrapObject(color = color, personality = personality,
                         user = wrap_user, top_tracks = top_tracks, top_artists = top_artists,
                         suggested_tracks= suggested_tracks)
    #print(new_wrap.top_artists[0].genres)
    return new_wrap