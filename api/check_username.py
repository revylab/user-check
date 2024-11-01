from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import os
from typing import Dict
import asyncio

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

async def check_github(client, username, headers):
    try:
        response = await client.get(f"https://github.com/{username}", headers=headers)
        return response.status_code == 404
    except:
        return None

async def check_twitter(client, username, headers):
    try:
        response = await client.get(f"https://twitter.com/{username}", headers=headers)
        return response.status_code == 404
    except:
        return None

async def check_instagram(client, username, headers):
    try:
        response = await client.get(f"https://www.instagram.com/{username}/", headers=headers)
        return "Profile Not Found" in response.text or "Page Not Found" in response.text
    except:
        return None

async def check_pinterest(client, username, headers):
    try:
        response = await client.get(f"https://pinterest.com/{username}/", headers=headers)
        return response.status_code == 404
    except:
        return None

async def check_linkedin(client, username, headers):
    try:
        response = await client.get(f"https://linkedin.com/in/{username}/", headers=headers)
        return response.status_code == 404
    except:
        return None

@app.get("/api/check/{username}")
async def check_username(username: str):
    username = username.lower()
    social_media = load_social_media_config()
    results = {}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        check_functions = {
            "github": check_github,
            "twitter": check_twitter,
            "instagram": check_instagram,
            "pinterest": check_pinterest,
            "linkedin": check_linkedin
        }
        
        for platform, config in social_media.items():
            try:
                check_function = check_functions.get(platform)
                if check_function:
                    is_available = await check_function(client, username, headers)
                    
                    if is_available is None:
                        status = "error"
                        message = "Tidak dapat mengecek username"
                    else:
                        status = "available" if is_available else "taken"
                        message = "Username tersedia" if is_available else "Username sudah digunakan"
                else:
                    status = "error"
                    message = "Platform tidak didukung"

                results[platform] = {
                    "status": status,
                    "message": message,
                    "url": config["url"].format(username=username) if status == "taken" else None,
                    "icon": config["icon"],
                    "platform_name": config["platform_name"]
                }
            except Exception as e:
                results[platform] = {
                    "status": "error",
                    "message": "Terjadi kesalahan saat mengecek",
                    "url": None,
                    "icon": config["icon"],
                    "platform_name": config["platform_name"]
                }
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
