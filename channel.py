from typing import List, Dict, Optional

import video


class Channel:
    def __init__(self, channel_name: str, channel_id: str, subscription_count: int,
               channel_views: int, channel_description: str, playlist_id: str,
               videos: Optional[Dict[str, video]] = None):
        self.channel_name = channel_name
        self.channel_id = channel_id
        self.subscription_count = subscription_count
        self.channel_views = channel_views
        self.channel_description = channel_description
        self.playlist_id = playlist_id
        self.videos = videos or {}

    def add_video(self, video_id: str, video: video):
        self.videos[video_id] = video

    def to_dict(self):
        return {
            "Channel_Name": {
                "Channel_Name": self.channel_name,
                "Channel_Id": self.channel_id,
                "Subscription_Count": self.subscription_count,
                "Channel_Views": self.channel_views,
                "Channel_Description": self.channel_description,
                "Playlist_Id": self.playlist_id
            },
            **{k: v.to_dict() for k, v in self.videos.items()}
        }
