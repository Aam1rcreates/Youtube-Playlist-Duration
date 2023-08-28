import os
import sys
import re
from googleapiclient.discovery import build
from datetime import timedelta
import requests


api_key = os.environ.get('youtube_api_key')

youtube = build('youtube', 'v3', developerKey=api_key)

# pls_request = youtube.playlists().list(
#     part='contentDetails, snippet',
#     channelId="UCX6OQ3DkcsbYNE6H8uQQuVA"
# )

# Use the regular expression to extract hors, min and sec from the duration which is in "PT14M47S" format
hours_pattern = re.compile(r'(\d+)H')
minutes_pattern = re.compile(r'(\d+)M')
seconds_pattern = re.compile(r'(\d+)S')

next_page_token = None

total_seconds=0

playlistId=''
if len(sys.argv) == 2:
    playlistId = sys.argv[1]
else:
    playlistId = "PLhQjrBD2T3817j24-GogXmWqO5Q5vYy0V"    

while True:
    # to request for particular playlist with it's id
    pl_request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlistId,
        maxResults=50,
        pageToken=next_page_token
    )

    pl_response = pl_request.execute()
    

    # Saving all the video's id in a list thatare present in the selected playlist
    vid_ids = []
    for item in pl_response['items']:
        vid_ids.append(item['contentDetails']['videoId'])

    vid_request = youtube.videos().list(
        part="contentDetails",
        id=','.join(vid_ids)
    )

    vid_response = vid_request.execute()


    # extract duration of video
    for item in vid_response['items']:
        duration = item['contentDetails']['duration']

        hours = hours_pattern.search(duration)
        minutes = minutes_pattern.search(duration)
        seconds = seconds_pattern.search(duration)

        hours = int(hours.group(1)) if hours else 0
        minutes = int(minutes.group(1)) if minutes else 0
        seconds = int(seconds.group(1)) if seconds else 0

        video_seconds = timedelta(
            hours = hours,
            minutes = minutes,
            seconds = seconds
        ).total_seconds()
        
        total_seconds += video_seconds

    next_page_token =pl_response.get('nextPageToken')

    if not next_page_token:
        break

total_seconds = int(total_seconds)

minutes, seconds = divmod(total_seconds, 60)
hours, minutes = divmod(minutes, 60)


print(f'This playlist is {hours}hr: {minutes}min: {seconds}sec long.')