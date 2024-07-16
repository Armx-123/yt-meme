import googleapiclient.discovery
import os

def get_subscriber_count(api_key, channel_id):
    # Create a resource object for interacting with the API
    youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)

    # Request to get channel details
    request = youtube.channels().list(
        part='statistics',
        id=channel_id
    )
    response = request.execute()

    # Extract the subscriber count from the response
    if 'items' in response and len(response['items']) > 0:
        subscriber_count = response['items'][0]['statistics']['subscriberCount']
        return subscriber_count
        print(subscriber_count)
    else:
        return 'Channel not found'

# Replace with your API key and the channel ID
api_key = os.environ['API']
channel_id = 'UCWmLyLVWoHZdz70Fpt2g6UQ'

subscriber_count = get_subscriber_count(api_key, channel_id)
print(f'The latest subscriber count is: {subscriber_count}')

