import os
import pysrt
import typesense


def init_search_client() -> typesense.Client:
    client = typesense.Client({
        "api_key": "xyz",
        "nodes": [{
            "host": "localhost",
            "port": "8108",
            "protocol": "http",
        }],
        "connection_timeout_seconds": 2.0,
    })
    return client

def init_collection(client: typesense.Client) -> None:
    init_collection_response = client.collections.create({
        "name": "educational_video_transcriptions",
        "fields": [
            {"name": "video_id", "type": "string"},
            {"name": "title", "type": "string"},
            {"name": "channel", "type": "string"},
            {"name": "upload_date", "type": "string"},
            {"name": "description", "type": "string"},
            {"name": "channel_follower_count", "int32"},
            {"name": "view_count", "int32"},
            {"name": "like_count", "int32"},
            {"name": "start_time", "type": "int32"},
            {"name": "end_time", "type": "int32"},
            {"name": "content", "type": "string"},
        ],
        "default_sorting_field": "publish_date",
    })
    print(f"Initialized new collection: {init_collection_response}")

def sync_caption_data_to_collection(client: typesense.Client) -> None:
    """TODO: Sync data from transcription files to typesense collection"""
    typesense_client = init_search_client()
    # Get all files from metadata directory
    metadata_dir = "metadata/"
    curr_path = os.getcwd()
    metadata_json_filepaths = sorted(os.listdir(os.path.join(curr_path, metadata_dir)))
    transcription_filepaths = sorted(os.listdir(os.path.join(curr_path, transcription_dir)))
    assert len(metadata_json_filepaths) == len(transcription_filepaths), f"# metadata files: {len(metadata_json_filepaths)} is different from # transcription files: {len(transcription_filepaths)}. Something went wrong in the bash script to transcribe audio!"
    video_data_filepaths = zip(metadata_json_filepaths, transcription_filepaths)
    for metadata_filepath, transcription_filepath in video_data_filepaths:
        # Parse metadata JSON
        with open(metadata_filepath, 'r') as fd:
            video_metadata = json.load(fd)
        # Parse transcription SRT files
        transcription_data = pysrt.open(transcription_filepath)
        # Create and upload to Typesense collection
        video_transcription_docs = [
            {
                "title": video_metadata["title"],
                "video_id": video_metadata["id"],
                "channel": video_metadata["channel"],
                "upload_date": video_metadata["upload_date"],
                "description": video_metadata["description"],
                "channel_follower_count": video_metadata["channel_follower_count"],
                "view_count": video_metadata["view_count"],
                "like_count": video_metadata["like_count"],
                "start_time": transcription_data.start.seconds,
                "end_time": transcription_data.end.seconds,
                "content": transcription_data.text
            }
            for video_metadata, transcription_data in zip(video_metadata, transcription_data)
        ]
        typesense_client.collections['educational_video_transcriptions'].documents.create(video_transcription_docs)
