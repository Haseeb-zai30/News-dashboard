import os
import json
import requests
import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient

def main(timer: func.TimerRequest):
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        raise ValueError("NEWS_API_KEY not set in Application Settings.")

    # Fetch headlines
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    resp = requests.get(url)
    headlines = resp.json().get("articles", [])

    # Prepare data
    data = [
        {
            "title": a["title"],
            "source": a["source"]["name"],
            "url": a["url"],
            "publishedAt": a["publishedAt"]
        }
        for a in headlines
    ]

    # Save to Blob Storage
    conn_str = os.getenv("AzureWebJobsStorage")
    blob_service = BlobServiceClient.from_connection_string(conn_str)
    container_name = "news-data"
    blob_client = blob_service.get_blob_client(
        container=container_name,
        blob=datetime.datetime.utcnow().strftime("%Y/%m/%d/%H/headlines.json")
    )

    blob_client.upload_blob(json.dumps(data), overwrite=True)
