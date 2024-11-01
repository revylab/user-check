from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import os
from typing import Dict

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load social media configurations
def load_social_media_config():
    with open('social_media.json') as f:
        return json.load(f)

@app.get("/api/check/{username}")
async def check_username(username: str):
    username = username.lower()
    social_media = load_social_media_config()
    results = {}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for platform, config in social_media.items():
            try:
                url = config["url"].format(username=username)
                response = await client.get(url, follow_redirects=True)
                
                # Check availability based on platform-specific logic
                available = False
                if platform == "github":
                    available = response.status_code == 404
                elif platform == "twitter":
                    available = response.status_code == 404
                elif platform == "instagram":
                    available = response.status_code == 404
                # Add more platform-specific checks as needed
                
                results[platform] = {
                    "available": available,
                    "url": config["url"].format(username=username),
                    "icon": config["icon"]
                }
            except Exception as e:
                results[platform] = {
                    "available": None,
                    "error": str(e),
                    "icon": config["icon"]
                }
    
    return results
