from typing import List, Dict, Optional

import comment


class Video:
    def __init__(self, video_id: str, video_name: str, video_description: str, tags: List[str],
                 published_at: str, view_count: int, like_count: int, dislike_count: int,
                 favorite_count: int, comment_count: int, duration: str, thumbnail: str,
                 caption_status: str, comments: Optional[Dict[str, comment]] = None
                 ):
        self.video_id = video_id
        self.video_name = video_name
        self.video_description = video_description
        self.tags = tags
        self.published_at = published_at
        self.view_count = view_count
        self.like_count = like_count
        self.dislike_count = dislike_count
        self.favorite_count = favorite_count
        self.comment_count = comment_count
        self.duration = duration
        self.thumbnail = thumbnail
        self.caption_status = caption_status
        self.comments = comments or {}

    def add_comment(self, comment_id: str, comment: comment):
        self.comments[comment_id] = comment

    def to_dict(self):
        return {
            "Video_Id": self.video_id,
            "Video_Name": self.video_name,
            "Video_Description": self.video_description,
            "Tags": self.tags,
            "PublishedAt": self.published_at,
            "View_Count": self.view_count,
            "Like_Count": self.like_count,
            "Dislike_Count": self.dislike_count,
            "Favorite_Count": self.favorite_count,
            "Comment_Count": self.comment_count,
            "Duration": self.duration,
            "Thumbnail": self.thumbnail,
            "Caption_Status": self.caption_status,
            "Comments": [comment_obj.to_dict() for comment_list in self.comments.values() for comment_obj in
                         comment_list]

        }
