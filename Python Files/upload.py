#!/usr/bin/python
'''Uploads a video to YouTube.'''

# Nono Martínez Alonso
# youtube.com/@NonoMartinezAlonso
# https://github.com/youtube/api-samples/blob/master/python/upload_video.py

import argparse
from http import client
import httplib2
import os
import random
import time
import pickle

import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

from comment.coment import comm
from comment.latest_video import get_latest_video

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
CLIENT_SECRETS_FILE = 'Data/client.json'

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
# json= "cretentials/Byte meme.json"
# pickl = "cretentials/Byte meme.json"
VALID_PRIVACY_STATUSES = ('public')

def get_authenticated_service():
    credentials = None

    if os.path.exists('Data/meme.pickle'):
        with open('Data/meme.pickle', 'rb') as token_file:
            credentials = pickle.load(token_file)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('Data/meme.pickle', 'wb') as token_file:
            pickle.dump(credentials, token_file)

    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def initialize_upload(youtube, options):
    tags = None
    if options.keywords:
        tags = options.keywords.split(',')

    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)


def resumable_upload(request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print('Uploading file...')
            status, response = request.next_chunk()
            if response is not None:
                if 'id' in response:
                    # comm(f"Leave a Like Subscribe !\n Thanks For Watching! :D","seal",get_latest_video("UC7bn2VFvK4JO-KQsHgtWmNw"))
                    print('Video id "%s" was successfully uploaded.' % response['id'])
                    with open("Data/Video.txt","w")as f:
                        f.write(response['id'])
                    
                else:
                    exit('The upload failed with an unexpected response: %s' % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = 'A retriable error occurred: %s' % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit('No longer attempting to retry.')

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print('Sleeping %f seconds and then retrying...' % sleep_seconds)
            time.sleep(sleep_seconds)


def main():
    default_file = "video.mp4"
    with open("Data/title.txt", "r") as f:
        default_title =f.readline() +" #fyp #funny #memes #shorts #trending"
    default_description = f" {default_title} \n#memes,#ylyl,#short\n\nfunny videos try not to laugh , funny memes try not to laugh , try not to laugh challenge meme, funny video funny video , memes that are actually funny , funny memes compilation , funny animal videos , try not to laugh challenge, funny memes , funny try not to laugh impossible memes , funny funny funny funny funny funny videos"
    default_category = "23"
    default_keywords = "dank memes,discord basement,funny,meme,memes compilation,memes from internet,memes from my discord,memes i found on discord,memes i stole from discord,memes that if ylyl,offensive memes,random memes,shorts,smallcat,tik tok memes,ylyl,you laugh you lose,the dank dealer,offensive memes 2021,kny memes,countryball memes,best minecraft memes"
    default_privacy_status = "public"  # Assuming "private" is a valid privacy status

    # Define the default values directly in the code
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--file", default=default_file, help="Video file to upload")
    argparser.add_argument("--title", default=default_title, help="Video title")
    argparser.add_argument("--description", default=default_description, help="Video description")
    argparser.add_argument("--category", default=default_category,
                           help="Numeric video category. See https://developers.google.com/youtube/v3/docs/videoCategories/list")
    argparser.add_argument("--keywords", default=default_keywords, help="Video keywords, comma separated")
    argparser.add_argument("--privacyStatus", default=default_privacy_status,
                           help="Video privacy status.")

    args = argparser.parse_args()

    if not os.path.exists(args.file):
        exit("Please specify a valid file using the --file parameter.")

    youtube = get_authenticated_service()
    try:
        initialize_upload(youtube, args)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

if __name__ == '__main__':
    main()
    with open("Data/Part.txt","r")as f:
        part =f.read()
    with open("Data/Part.txt","w")as f:
        f.write((str)((int)(part)+1))
