class Comment:
    def __init__(self, comment_id: str, comment_text: str, comment_author: str, comment_published_at: str):
        self.comment_id = comment_id
        self.comment_text = comment_text
        self.comment_author = comment_author
        self.comment_published_at = comment_published_at

    def to_dict(self):
        return {
            "Comment_Id": self.comment_id,
            "Comment_Text": self.comment_text,
            "Comment_Author": self.comment_author,
            "Comment_PublishedAt": self.comment_published_at
        }
