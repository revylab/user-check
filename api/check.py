# api/check.py
from http.client import HTTPConnection, HTTPSConnection
import json
from typing import Dict, List
import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Load social media platforms configuration
with open('platforms.json') as f:
    PLATFORMS = json.load(f)

class UsernameRequest(BaseModel):
    username: str

async def check_username(session: aiohttp.ClientSession, platform: Dict, username: str) -> Dict:
    try:
        url = platform['url'].format(username=username)
        headers = platform.get('headers', {})
        
        async with session.get(url, headers=headers, allow_redirects=False) as response:
            exists = response.status != 404
            
            return {
                'platform': platform['name'],
                'exists': exists,
                'url': url if exists else None
            }
    except Exception as e:
        print(f"Error checking {platform['name']}: {str(e)}")
        return {
            'platform': platform['name'],
            'exists': None,
            'error': str(e)
        }

@app.post("/api/check")
async def check_availability(request: UsernameRequest):
    if not request.username or len(request.username) < 1:
        raise HTTPException(status_code=400, detail="Username is required")
        
    async with aiohttp.ClientSession() as session:
        tasks = []
        for platform in PLATFORMS:
            task = check_username(session, platform, request.username)
            tasks.append(task)
            
        results = await asyncio.gather(*tasks)
        
        # Filter out errors and sort by platform name
        valid_results = [r for r in results if r['exists'] is not None]
        valid_results.sort(key=lambda x: x['platform'])
        
        return valid_results
