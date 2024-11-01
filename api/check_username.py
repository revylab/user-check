from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import os
from typing import Dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_social_media_config():
    with open('social_media.json') as f:
        return json.load(f)

@app.get("/api/check/{username}")
async def check_username(username: str):
    username = username.lower()
    social_media = load_social_media_config()
    results = {}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for platform, config in social_media.items():
            try:
                url = config["url"].format(username=username)
                response = await client.get(url, headers=headers, follow_redirects=True)
                
                available = False
                error_message = None
                
                if platform == "github":
                    available = response.status_code == 404
                elif platform == "twitter":
                    # Twitter now X requires authentication, marking as unknown
                    error_message = "Requires authentication"
                elif platform == "instagram":
                    # Instagram requires authentication
                    error_message = "Requires authentication"
                elif platform == "pinterest":
                    # Pinterest needs special handling
                    error_message = "Requires authentication"
                elif platform == "linkedin":
                    # LinkedIn needs authentication
                    error_message = "Requires authentication"
                
                results[platform] = {
                    "available": available if error_message is None else None,
                    "error_message": error_message,
                    "url": url if not error_message and not available else None,
                    "icon": config["icon"],
                    "platform_name": config["platform_name"]
                }
            except Exception as e:
                results[platform] = {
                    "available": None,
                    "error_message": "Connection error",
                    "url": None,
                    "icon": config["icon"],
                    "platform_name": config["platform_name"]
                }
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
