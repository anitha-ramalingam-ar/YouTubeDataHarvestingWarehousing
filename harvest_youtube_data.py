import requests
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from channel import Channel
from video import Video
from comment import Comment


class YouTubeInfo:

    def __init__(self, api_key, channel_id, connection, channel):
        self.api_key = api_key
        self.channel_id = channel_id
        self.channel = channel
        self.connection = connection

    def get_channel_basic_info(self):
        print("Inside Channel Basic Info")

        global channel
        get_channel_url = f'https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics,contentDetails&id={self.channel_id}&key={self.api_key}'

        channel_json_response = requests.get(get_channel_url)
        channel_data = json.loads(channel_json_response.text)

        try:
            channel = Channel(channel_data["items"][0]["snippet"]["title"],
                              channel_data["items"][0]["id"],
                              channel_data["items"][0]["statistics"]["subscriberCount"],
                              channel_data["items"][0]["statistics"]["viewCount"],
                              channel_data["items"][0]["snippet"]["description"],
                              channel_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"])

            self.write_channel_info_into_sql(channel)
            channel = self.get_playlist_info(channel)
            print("Exist Channel Basic Info")

        except Exception as e:
            print(f"An error occurred: {e}")

        self.channel = channel

    def write_channel_info_into_sql(self, channel):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO CHANNEL (CHANNEL_ID, CHANNEL_NAME, CHANNEL_TYPE, CHANNEL_VIEWS, CHANNEL_DESCRIPTION, CHANNEL_STATUS) VALUES (?, ?, ?, ?, ?, ?)",
                (channel.channel_id,
                 channel.channel_name,
                 "CHANNEL_TYPE",
                 channel.channel_views,
                 channel.channel_description,
                 "CHANNEL_STATUS")
            )
            self.connection.commit()
            print("Write into Channel table completed")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_playlist_info(self, channel):
        get_playlist_url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails,id,snippet,status&playlistId={channel.playlist_id}&key={self.api_key}'

        playlist_json_response = requests.get(get_playlist_url)
        playlist_data = json.loads(playlist_json_response.text)

        try:
            for i, item in enumerate(playlist_data["items"], start=1):
                video_id = item["snippet"]["resourceId"]["videoId"]
                channel.add_video("Video_Id_" + str(i), self.get_video_details(video_id, channel.playlist_id))
                self.write_playlist_info_into_sql(channel)

        except Exception as e:
            print(f"An error occurred: {e}")

        return channel

    def write_playlist_info_into_sql(self, channel):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO PLAYLIST (PLAYLIST_ID, CHANNEL_ID, PLAYLIST_NAME) VALUES (?, ?, ?)",
                (channel.playlist_id,
                 channel.channel_id,
                 "PLAYLIST_NAME")
            )
            self.connection.commit()
            print("Write into Playlist table completed")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_video_details(self, video_id, playlist_id):
        get_video_url = f'https://www.googleapis.com/youtube/v3/videos?part=contentDetails,id,snippet,status,statistics&id={video_id}&key={self.api_key}'

        video_json_response = requests.get(get_video_url)
        video_data = json.loads(video_json_response.text)

        video = Video(video_data["items"][0]["id"],
                      video_data["items"][0]["snippet"]["title"],
                      video_data["items"][0]["snippet"]["description"],
                      video_data["items"][0]["snippet"]["tags"],
                      video_data["items"][0]["snippet"]["publishedAt"],
                      video_data["items"][0]["statistics"]["viewCount"],
                      video_data["items"][0]["statistics"]["likeCount"],
                      0,
                      video_data["items"][0]["statistics"]["favoriteCount"],
                      video_data["items"][0]["statistics"]["commentCount"],
                      video_data["items"][0]["contentDetails"]["duration"],
                      video_data["items"][0]["snippet"]["thumbnails"]["standard"]["url"],
                      video_data["items"][0]["contentDetails"]["caption"],
                      self.get_video_comments_details(video_id)
                      )
        self.write_videos_info_into_sql(video, playlist_id)
        return video

    def write_videos_info_into_sql(self, video, playlist_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO VIDEO (VIDEO_ID, PLAYLIST_ID, VIDEO_NAME, VIDEO_DESCRIPTION, PUBLISHED_DATE, VIEW_COUNT, "
                "LIKE_COUNT, DISLIKE_COUNT, FAVORITE_COUNT, COMMENT_COUNT, DURATION, THUMBNAIL, CAPTION_STATUS) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (video.video_id,
                 playlist_id,
                 video.video_name,
                 video.video_description,
                 video.published_at,
                 video.view_count,
                 video.like_count,
                 video.dislike_count,
                 video.favorite_count,
                 video.comment_count,
                 video.duration,
                 video.thumbnail,
                 video.caption_status)
            )
            self.connection.commit()
            print("Write into Video table completed")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_video_comments_details(self, video_id):
        global comments
        get_comments_url = f'https://www.googleapis.com/youtube/v3/commentThreads?key={self.api_key}&textFormat=plainText&part=snippet&videoId={video_id}&maxResults=50'

        comments_json_response = requests.get(get_comments_url)
        comments_data = json.loads(comments_json_response.text)

        try:
            comments = {}
            for i, item in enumerate(comments_data["items"], start=1):
                comment_id = item["snippet"]["topLevelComment"]["id"]
                comment = Comment(
                    comment_id,
                    item["snippet"]["topLevelComment"]["snippet"]["textOriginal"],
                    item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                    item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                )
                self.write_comments_info_into_sql(video_id, comment)
                comments[comment_id] = []
                comments[comment_id].append(comment)
        except Exception as e:
            print(f"An error occurred: {e}")

        return comments

    def write_comments_info_into_sql(self, video_id, comment):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO COMMENT (COMMENT_ID, VIDEO_ID, COMMENT_TEXT, COMMENT_AUTHOR, COMMENT_PUBLISHED_DATE) VALUES (?, ?, ?, ?, ?)",
                (comment.comment_id,
                 video_id,
                 comment.comment_text,
                 comment.comment_author,
                 comment.comment_published_at)
            )
            self.connection.commit()
            print("Write into Comment table completed")
        except Exception as e:
            print(f"An error occurred: {e}")

    def write_into_mongodb(self):
        mongo_uri = "mongodb+srv://admin:admin@cluster0.mfk95pn.mongodb.net/?retryWrites=true&w=majority"

        client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        db = client['youtube_channels_db']
        youtube_channels = db['youtube_channels']

        try:
            youtube_channels.insert_one(self.channel.to_dict())
            print("Inserted into MongoDB successfully")
        except Exception as e:
            print(f"An error occurred: {e}")

        client.close()
