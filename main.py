import sqlite3
import streamlit as st

import channel
from harvest_youtube_data import YouTubeInfo

connection = sqlite3.connect("youtube.db", timeout=10)


def create_sql_table():
    create_channel_table = "CREATE TABLE IF NOT EXISTS CHANNEL (CHANNEL_ID VARCHAR(255), CHANNEL_NAME VARCHAR(255), CHANNEL_TYPE VARCHAR(255), CHANNEL_VIEWS INT, CHANNEL_DESCRIPTION TEXT, CHANNEL_STATUS VARCHAR(255))"
    create_playlist_table = "CREATE TABLE IF NOT EXISTS PLAYLIST (PLAYLIST_ID VARCHAR(255), CHANNEL_ID VARCHAR(255), PLAYLIST_NAME VARCHAR(255))"
    create_video_table = "CREATE TABLE IF NOT EXISTS VIDEO (VIDEO_ID VARCHAR(255), PLAYLIST_ID VARCHAR(255), VIDEO_NAME VARCHAR(255), VIDEO_DESCRIPTION TEXT, PUBLISHED_DATE DATETIME, VIEW_COUNT INT, LIKE_COUNT INT, DISLIKE_COUNT INT, FAVORITE_COUNT INT, COMMENT_COUNT INT, DURATION INT, THUMBNAIL VARCHAR(255), CAPTION_STATUS VARCHAR(255))"
    create_comment_table = "CREATE TABLE IF NOT EXISTS COMMENT (COMMENT_ID VARCHAR(255), VIDEO_ID VARCHAR(255), COMMENT_TEXT TEXT, COMMENT_AUTHOR VARCHAR(255), COMMENT_PUBLISHED_DATE DATETIME)"

    cursor = connection.cursor()
    cursor.execute(create_channel_table)
    cursor.execute(create_playlist_table)
    cursor.execute(create_video_table)
    cursor.execute(create_comment_table)
    print("DB Changes : ", connection.total_changes)


def collect_youtube_data(channel_list):
    create_sql_table()

    api_key = "AIzaSyAAIl72c5gIw0niTvZT1LEcBXP2W2zhupM"
    # channels = ["UC5wuaJnklgYnbJIeTVhPWug",
    #             "UCMyi2FZAUNLFDUE8ZIf7YOQ",
    #             "UCoDGpjcVMTGF161PZJenTNw",
    #             "UCeP4oj6TsUlnlzQqUzKxUjg",
    #             "UCnz - ZXXER4jOvuED5trXfEA",
    #             "UCpnJuQkNm9j9R7LCqWtf56g",
    #             "UC5_4POQX0WtMhUpRsh - YQhA",
    #             "UCVlNQ5Olu3Uiv5FL8e - yEmQ",
    #             "UCTbgC5uNJVjpMPDkO1OYY7w",
    #             "UCu - Fi_6fJyytxb - julK - qNg"]
    channels = channel_list.split(",")
    print(channels)

    for channel_id in channels:
        yt = YouTubeInfo(api_key, channel_id, connection, channel=channel)
        yt.get_channel_basic_info()
        yt.write_into_mongodb()

    return connection


def main():
    channel_input = st.text_input('Please Enter List of YouTube IDs', '')

    if st.button("Collect Data"):
        if channel_input:
            collect_youtube_data(channel_input)
            st.divider()
            st.text('Data Harvested Successfully')
            st.divider()

    if channel_input:
        option = st.selectbox(
            'Please Select An Option From the Dropdown List to See the Results',
            ('',
             '1. What are the names of all the videos and their corresponding channels?',
             '2. Which channels have the most number of videos, and how many videos do they have?',
             '3. What are the top 10 most viewed videos and their respective channels?',
             '4. How many comments were made on each video, and what are their corresponding channel names?',
             '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
             '6. What is the total number of likes and dislikes for each video, and what are their corresponding channel names?',
             '7. What is the total number of views for each channel, and what are their corresponding channel names?',
             '8. What are the names of all the channels that have published videos in the year 2022?',
             '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
             '10.Which videos have the highest number of comments, and what are their corresponding channel names?'))

        option = str(option)

        if option.startswith("1"):
            result = connection.cursor().execute(
                "SELECT V.VIDEO_NAME, C.CHANNEL_NAME FROM VIDEO AS V JOIN PLAYLIST P ON V.PLAYLIST_ID = P.PLAYLIST_ID JOIN CHANNEL C ON P.CHANNEL_ID = C.CHANNEL_ID GROUP BY V.VIDEO_NAME").fetchall()
            st.table(result)
        elif option.startswith("2"):
            result = connection.cursor().execute(
                "SELECT C.CHANNEL_NAME, COUNT(V.VIDEO_ID) AS NUM_OF_VIDEOS FROM CHANNEL C JOIN PLAYLIST P ON C.CHANNEL_ID = P.CHANNEL_ID JOIN VIDEO V ON P.PLAYLIST_ID = V.PLAYLIST_ID GROUP BY C.CHANNEL_NAME ORDER BY NUM_OF_VIDEOS DESC").fetchall()
            st.table(result)
        elif option.startswith("3"):
            result = connection.cursor().execute(
                "SELECT V.VIDEO_NAME, C.CHANNEL_NAME, V.VIEW_COUNT FROM VIDEO V JOIN PLAYLIST P ON V.PLAYLIST_ID = P.PLAYLIST_ID JOIN CHANNEL C ON P.CHANNEL_ID = C.CHANNEL_ID ORDER BY V.VIEW_COUNT DESC LIMIT 10").fetchone()
            st.table(result)
        elif option.startswith("4"):
            result = connection.cursor().execute(
                "SELECT V.VIDEO_NAME, C.CHANNEL_NAME, COUNT(COM.COMMENT_ID) AS NUM_OF_COMMENTS FROM VIDEO V JOIN PLAYLIST P ON V.PLAYLIST_ID = P.PLAYLIST_ID JOIN CHANNEL C ON P.CHANNEL_ID = C.CHANNEL_ID LEFT JOIN COMMENT COM ON V.VIDEO_ID = COM.VIDEO_ID GROUP BY V.VIDEO_NAME, C.CHANNEL_NAME ORDER BY NUM_OF_COMMENTS DESC").fetchall()
            st.table(result)
        elif option.startswith("5"):
            result = connection.cursor().execute(
                "SELECT V.VIDEO_NAME, C.CHANNEL_NAME, V.LIKE_COUNT FROM VIDEO V JOIN PLAYLIST P ON V.PLAYLIST_ID = P.PLAYLIST_ID JOIN CHANNEL C ON P.CHANNEL_ID = C.CHANNEL_ID GROUP BY V.LIKE_COUNT ORDER BY V.LIKE_COUNT DESC").fetchall()
            st.table(result)
        elif option.startswith("6"):
            result = connection.cursor().execute(
                "SELECT V.VIDEO_NAME, C.CHANNEL_NAME, V.LIKE_COUNT, V.DISLIKE_COUNT FROM VIDEO V JOIN PLAYLIST P ON V.PLAYLIST_ID = P.PLAYLIST_ID JOIN CHANNEL C ON P.CHANNEL_ID = C.CHANNEL_ID GROUP BY V.LIKE_COUNT ORDER BY V.LIKE_COUNT DESC, V.DISLIKE_COUNT DESC").fetchall()
            st.table(result)
        elif option.startswith("7"):
            result = connection.cursor().execute(
                "SELECT C.CHANNEL_NAME, SUM(V.VIEW_COUNT) AS TOTAL_VIEWS FROM CHANNEL C JOIN PLAYLIST P ON C.CHANNEL_ID = P.CHANNEL_ID JOIN VIDEO V ON P.PLAYLIST_ID = V.PLAYLIST_ID GROUP BY C.CHANNEL_NAME ORDER BY TOTAL_VIEWS DESC").fetchall()
            st.table(result)
        elif option.startswith("8"):
            result = connection.cursor().execute(
                "SELECT DISTINCT C.CHANNEL_NAME FROM CHANNEL C JOIN PLAYLIST P ON C.CHANNEL_ID = P.CHANNEL_ID JOIN VIDEO V ON P.PLAYLIST_ID = V.PLAYLIST_ID WHERE strftime('%Y', V.PUBLISHED_DATE) = '2022'").fetchall()
            st.table(result)
        elif option.startswith("9"):
            result = connection.cursor().execute(
                "SELECT C.CHANNEL_NAME, AVG(V.DURATION) AS AVERAGE_DURATION FROM CHANNEL C JOIN PLAYLIST P ON C.CHANNEL_ID = P.CHANNEL_ID JOIN VIDEO V ON P.PLAYLIST_ID = V.PLAYLIST_ID GROUP BY C.CHANNEL_NAME ORDER BY AVERAGE_DURATION DESC").fetchall()
            st.table(result)
        elif option.startswith("10"):
            result = connection.cursor().execute(
                "SELECT V.VIDEO_NAME, C.CHANNEL_NAME, COUNT(COM.COMMENT_ID) AS NUM_OF_COMMENTS FROM VIDEO V JOIN PLAYLIST P ON V.PLAYLIST_ID = P.PLAYLIST_ID JOIN CHANNEL C ON P.CHANNEL_ID = C.CHANNEL_ID LEFT JOIN COMMENT COM ON V.VIDEO_ID = COM.VIDEO_ID GROUP BY V.VIDEO_NAME, C.CHANNEL_NAME ORDER BY NUM_OF_COMMENTS DESC").fetchall()
            st.table(result)


if __name__ == "__main__":
    main()
