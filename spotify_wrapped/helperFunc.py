from spotify_wrapped.Spotify import Track, WrapObject
from spotify_wrapped.models import Track, Artist, Wrap, User

def convert_tuple_to_dict(tuple_list):
    return {key:value for (key,value) in tuple_list}

def convert_track_object_to_track_model(track_obj):
    #print(track_obj.__str__())
    album_name = track_obj.album_name
    album_image = track_obj.album_image
    name = track_obj.name
    artists = track_obj.artists
    new_track = Track(album_name=album_name, album_image=album_image, track_name=name, artist_list=artists)
    new_track.save()
    return new_track


def convert_artist_object_to_artist_model(artist_obj):
    name = artist_obj.name
    image = artist_obj.image
    artist_id = artist_obj.id
    genres = artist_obj.genres
    new_artist = Artist(id = artist_id, name = name, image = image, genres = genres)
    new_artist.save()
    return new_artist

def convert_user_object_to_user_model(user_obj):
    display_name = user_obj.display_name
    user_id = user_obj.id
    pfp = user_obj.pfp
    product = user_obj.product
    uri = user_obj.uri
    new_user = User(display_name = display_name, id = user_id, product = product, uri = uri, pfp = pfp)
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
    new_wrap = Wrap(user = user,color = color, personality = personality,
                    top_audio = top_audio, top_genres=top_genres)
    new_wrap.save()
    new_wrap.top_tracks.add(*top_tracks)
    new_wrap.top_artists.add(*top_artists)
    new_wrap.suggested_tracks.add(*suggested_tracks)
    return new_wrap

