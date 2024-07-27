#!/usr/bin/python3

import os
import time
import random
import sys
import pickle
import argparse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Explicitly tell the underlying HTTP transport library not to retry, since we are handling retry logic ourselves.
import httplib2
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib2.ServerNotFoundError)

# Always retry when an apiclient.errors.HttpError with one of these status codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# CLIENT_SECRETS_FILE, name of a file containing the OAuth 2.0 information for this application.
CLIENT_SECRETS_FILE = "Data/client.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_authenticated_service():
    creds = None
    if os.path.exists('credentials/seal.pickle'):
        with open('credentials/seal.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('credentials/seal.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=creds)

def upload_banner(image_file):
    try:
        service = get_authenticated_service()
        request = service.channelBanners().insert(
            body={},
            media_body=MediaFileUpload(image_file)
        )
        response = request.execute()
        return response.get('url')
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def set_banner(service, banner_url):
    try:
        channels_response = service.channels().list(
            mine=True,
            part="brandingSettings"
        ).execute()

        branding_settings = channels_response["items"][0]["brandingSettings"]
        if "image" not in branding_settings:
            branding_settings["image"] = {}

        branding_settings["image"]["bannerExternalUrl"] = banner_url

        channels_update_response = service.channels().update(
            part='brandingSettings',
            body={
                'id': channels_response["items"][0]["id"],
                'brandingSettings': branding_settings
            }
        ).execute()

        updated_branding_settings = channels_update_response.get("brandingSettings", {})
        if updated_branding_settings and "image" in updated_branding_settings:
            banner_mobile_url = updated_branding_settings["image"].get("bannerMobileImageUrl")
            if banner_mobile_url:
                print(f"Banner is set to '{banner_mobile_url}'.")
            else:
                print(f"Banner is set to '{banner_url}'.")
        else:
            print(f"Banner is set to '{banner_url}'.")
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    image_file_path = "composite_image.png"
    if not os.path.exists(image_file_path):
        sys.exit(f"The specified file '{image_file_path}' does not exist.")

    banner_url = upload_banner(image_file_path)
    if banner_url:
        service = get_authenticated_service()
        set_banner(service, banner_url)
    else:
        print("Failed to upload the banner.")
