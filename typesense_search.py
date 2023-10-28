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
            {"name": "title", "type": "string"},
            {"name": "channel_name", "type": "string"},
            {"name": "publish_date", "type": "string"},
            {"name": "start_time", "type": "int32"},
            {"name": "end_time", "type": "int32"},
            {"name": "content", "type": "string"},
        ],
        "default_sorting_field": "publish_date",
    })
    print(f"Initialized new collection: {init_collection_response}")

def sync_caption_data_to_collection(client: typesense.Client) -> None:
    """TODO: Sync data from transcription files to typesense collection"""
    pass
