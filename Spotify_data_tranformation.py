import json
import boto3
import pandas as pd
from datetime import datetime
from io import StringIO


def album(data):
    album_list = []
    for row in data["items"]:
      album_id = row["track"]["album"]["id"]
      album_name = row["track"]["album"]["name"]
      album_release_date = row["track"]["album"]["release_date"]
      album_total_tracks = row["track"]["album"]["total_tracks"]
      album_external_url = row["track"]["album"]["external_urls"]["spotify"]
      album_elements = {"album_id" : album_id, "album_name" : album_name, "album_release_date" : album_release_date, "album_total_tracks" : album_total_tracks, "album_external_url" : album_external_url}  
    
      album_list.append(album_elements)

    return album_list

def artist(data):
    artist_list = []

    for row in data["items"]:
        for key, value in row.items():
            if key == "track":
                 for artist in value["artists"]:
                  artist_dict =  {"artist_id" : artist["id"], "artist_name" : artist["name"], "external_url" : artist["href"]}
                  artist_list.append(artist_dict) 
  
    return artist_list

def song(data):
    song_list = []  

    for row in data["items"]:
      song_id = row["track"]["id"]
      song_name = row["track"]["name"]
      song_duration_ms = row["track"]["duration_ms"]
      song_popularity = row["track"]["popularity"]
      song_url = row["track"]["external_urls"]["spotify"]
      song_added = row["added_at"]
      album_id = row["track"]["album"]["id"]
      artist_id = row["track"]["artists"][0]["id"]
      song_elements = {"song_id" : song_id, "song_name" : song_name, "song_duration_ms" : song_duration_ms, "song_popularity" : song_popularity, "song_url" : song_url, "song_added" : song_added, "album_id" : album_id, "artist_id" : artist_id}

    song_list.append(song_elements)

    return song_list


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    Bucket = "spotify-etl-project-billy"
    Key = "raw_data/to_process"

    spotify_data = []
    spotify_key = []
    for file in s3.list_objects(Bucket=Bucket, Prefix=Key)["Contents"]:
        file_key = file["Key"] 
        if file_key.split(".")[-1] == "json":
            response = s3.get_object(Bucket=Bucket, Key=file_key)
            content = response["Body"]
            jsonObject = json.loads(content.read())
            spotify_data.append(jsonObject)
            spotify_key.append(file_key)


    for data in spotify_data:
        album_list = album(data)
        artist_list = artist(data)
        song_list = song(data)
        
        album_df = pd.DataFrame.from_dict(artist_list) 
        

        artist_df = pd.DataFrame.from_dict(artist_list)
        artist_df = artist_df.drop_duplicates(subset=["artist_id"])

        song_df = pd.DataFrame.from_dict(song_list)

        
        song_df["song_added"] = pd.to_datetime(song_df["song_added"])

        song_key = "transformed_data/songs_data/song_transformed_" + str(datetime.now()) + ".csv"
        song_buffer = StringIO()
        song_df.to_csv(song_buffer)
        song_content = song_buffer.getvalue()
        s3.put_object(Bucket=Bucket, Key=song_key, Body=song_content)

        album_key = "transformed_data/album_df_data/album_df_transformed_" + str(datetime.now()) + ".csv"
        album_buffer = StringIO()
        album_df.to_csv(album_buffer)
        album_content = album_buffer.getvalue()
        s3.put_object(Bucket=Bucket, Key=album_key, Body=album_content)

        artist_key = "transformed_data/artist_data/artist_transformed_" + str(datetime.now()) + ".csv"
        artist_buffer = StringIO()
        artist_df.to_csv(artist_buffer)
        artist_content = artist_buffer.getvalue()
        s3.put_object(Bucket=Bucket, Key=artist_key, Body=artist_content)


    s3_resource = boto3.resource('s3')
    for key in spotify_key:
        copy_source = {
        'Bucket': Bucket,
        'Key': key
        }
        s3_resource.meta.client.copy(copy_source, Bucket, 'raw_data/processed/' + key.split("/")[-1])
        s3_resource.Object(Bucket, key).delete()