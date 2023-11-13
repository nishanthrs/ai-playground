import json
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
    video_transcription_schema = {
        "name": "educational_video_transcriptions",
        "fields": [
            {"name": "video_id", "type": "string"},
            {"name": "title", "type": "string"},
            {"name": "channel", "type": "string"},
            {"name": "upload_date", "type": "string"},
            {"name": "channel_follower_count", "type": "int32"},
            {"name": "view_count", "type": "int32"},
            {"name": "like_count", "type": "int32"},
            {"name": "start_time", "type": "int32"},
            {"name": "end_time", "type": "int32"},
            {"name": "content", "type": "string"},
        ],
        "default_sorting_field": "channel_follower_count",
    }
    init_collection_response = client.collections.create(video_transcription_schema)
    print(f"Initialized new collection: {init_collection_response}")

def sync_caption_data_to_collection(client: typesense.Client) -> None:
    """Index data from transcription files to typesense collection"""
    # Get all files from metadata directory
    metadata_dir = "metadata/"
    transcription_dir = "transcriptions/"
    metadata_json_filepaths = [os.path.join(metadata_dir, filename) for filename in sorted(os.listdir(metadata_dir))]
    transcription_filepaths = [os.path.join(transcription_dir, filename) for filename in sorted(os.listdir(transcription_dir))]

    metadata_filenames = [os.path.basename(filename).rsplit('.', maxsplit=1)[0].rsplit('.', maxsplit=1)[0] for filename in metadata_json_filepaths]
    transcription_filenames = [os.path.basename(filename).rsplit('.', maxsplit=1)[0] for filename in transcription_filepaths]
    print(
        f"Metadata but not in transcriptions: {len(metadata_filenames), len(transcription_filenames), set(metadata_filenames) - set(transcription_filenames), set(transcription_filenames) - set(metadata_filenames)}"
    )
    # NOTE: When downloading playlists, the playlist metadata is downloaded as well. Thus, the # metadata files = # playlists + # transcriptions
    # We should just log this info, but not throw an error here.
    # assert len(metadata_json_filepaths) == len(transcription_filepaths), f"# metadata files: {len(metadata_json_filepaths)} is different from # transcription files: {len(transcription_filepaths)}. Something went wrong in the bash script to transcribe audio!"

    # video_data_filepaths = zip(metadata_json_filepaths, transcription_filepaths)
    for transcription_filepath in transcription_filepaths:
        filename = os.path.basename(transcription_filepath).rsplit('.', maxsplit=1)[0]
        metadata_filepath = metadata_json_filepaths[
            metadata_json_filepaths.index(f"{os.path.join(metadata_dir, filename + '.info.json')}")
        ]
        # Parse metadata JSON
        with open(metadata_filepath, 'r') as fd:
            video_metadata = json.load(fd)
        # Parse transcription SRT files
        transcription_data = pysrt.open(transcription_filepath)
        # Create and upload to Typesense collection
        try:
            video_transcription_docs = [
                {
                    "video_id": video_metadata["id"],
                    "title": video_metadata["title"],
                    "channel": video_metadata["channel"],
                    "upload_date": video_metadata["upload_date"],
                    "channel_follower_count": video_metadata["channel_follower_count"],
                    "view_count": video_metadata["view_count"],
                    "like_count": video_metadata["like_count"],
                    "start_time": (sub.start.hours * 3600) + (sub.start.minutes * 60) + sub.start.seconds,
                    "end_time": (sub.end.hours * 3600) + (sub.end.minutes * 60) + sub.end.seconds,
                    "content": sub.text
                }
                for sub in transcription_data
            ]
        except KeyError as e:
            print(f"Could not find key {e} in metadata file {metadata_filepath}. Skipping this video.")

        typesense_client.collections["educational_video_transcriptions"].documents.import_(video_transcription_docs, {"action": "upsert"})


if __name__ == "__main__":
    typesense_client = init_search_client()
    # typesense_client.collections["educational_video_transcriptions"].delete()
    try:
        init_collection(typesense_client)
    except typesense.exceptions.ObjectAlreadyExists:
        pass
    sync_caption_data_to_collection(typesense_client)
    search_data = typesense_client.collections["educational_video_transcriptions"].documents.search({"q": "GNU parallel", "query_by": "content", "sort_by": "start_time:asc"})
    print(f"{search_data['found']} search results for GNU parallel:")
    for doc_data in search_data['hits']:
        doc = doc_data['document']
        print(f"{doc['start_time']} - {doc['end_time']}: {doc['content']}")
    # print(f"{search_data['found']} search results for GNU parallel: {[(doc['document']['start_time'], doc['document']['end_time'], doc['document']['content']) for doc in search_data['hits']]}")
