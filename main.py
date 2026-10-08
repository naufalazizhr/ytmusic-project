from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ytmusic = YTMusic()

# 1. Endpoint Beranda / Top Hits
@app.get("/home")
def get_home_recommendations():
    try:
        results = ytmusic.search("Top Hits", filter="songs")
        songs = []
        for item in results[:10]:
            songs.append({
                "id": item.get("videoId"),
                "title": item.get("title"),
                "artist": item["artists"][0]["name"] if item.get("artists") else "Unknown",
                "thumbnail": item["thumbnails"][-1]["url"] if item.get("thumbnails") else ""
            })
        return {"results": songs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Endpoint Pencarian
@app.get("/search")
def search_songs(q: str):
    try:
        results = ytmusic.search(q, filter="songs")
        songs = []
        for item in results:
            songs.append({
                "id": item.get("videoId"),
                "title": item.get("title"),
                "artist": item["artists"][0]["name"] if item.get("artists") else "Unknown",
                "thumbnail": item["thumbnails"][-1]["url"] if item.get("thumbnails") else ""
            })
        return {"results": songs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Endpoint Extraction Stream Audio
@app.get("/stream/{video_id}")
def get_stream_url(video_id: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {"stream_url": info['url']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. ALGORITMA YTMUSIC: Lagu terkait / Radio (Thumbnail Fix)
@app.get("/related/{video_id}")
def get_related_songs(video_id: str):
    try:
        watch_playlist = ytmusic.get_watch_playlist(videoId=video_id, limit=10)
        tracks = watch_playlist.get("tracks", [])
        songs = []
        for item in tracks[1:]: # Lewati index 0 (lagu sedang diputar)
            thumb_url = ""
            if item.get("thumbnail"):
                thumb_url = item["thumbnail"][-1]["url"] if isinstance(item["thumbnail"], list) else item["thumbnail"]
            elif item.get("thumbnails"):
                thumb_url = item["thumbnails"][-1]["url"] if isinstance(item["thumbnails"], list) else item["thumbnails"]

            songs.append({
                "id": item.get("videoId"),
                "title": item.get("title"),
                "artist": item["artists"][0]["name"] if item.get("artists") else "Unknown",
                "thumbnail": thumb_url
            })
        return {"results": songs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))