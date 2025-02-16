from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio
import logging
import aiohttp
import re
import json
from urllib.parse import quote
import traceback

logger = logging.getLogger(__name__)

def parse_duration(duration_text: str) -> int:
    """Convert duration text to seconds."""
    if not duration_text:
        return 0
    
    # Convert "1:23" or "12:34" to seconds
    parts = duration_text.split(":")
    if len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    elif len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    return 0

def parse_view_count(view_text: str) -> int:
    """Convert view count text to number."""
    if not view_text:
        return 0
    
    # Remove "views", "K", "M", etc and convert to number
    number = ''.join(filter(str.isdigit, view_text.split()[0]))
    multiplier = 1
    if 'K' in view_text:
        multiplier = 1000
    elif 'M' in view_text:
        multiplier = 1000000
    
    try:
        return int(number) * multiplier if number else 0
    except ValueError:
        return 0

def parse_relative_time(time_text: str) -> datetime:
    """Convert relative time text to datetime."""
    now = datetime.now()
    
    if not time_text:
        return now
    
    time_text = time_text.lower()
    number = int(''.join(filter(str.isdigit, time_text.split()[0])))
    
    if 'second' in time_text:
        return now - timedelta(seconds=number)
    elif 'minute' in time_text:
        return now - timedelta(minutes=number)
    elif 'hour' in time_text:
        return now - timedelta(hours=number)
    elif 'day' in time_text:
        return now - timedelta(days=number)
    elif 'week' in time_text:
        return now - timedelta(weeks=number)
    elif 'month' in time_text:
        return now - timedelta(days=number * 30)
    elif 'year' in time_text:
        return now - timedelta(days=number * 365)
    
    return now

def calculate_video_score(video: Dict[str, Any], search_mode: str = 'balanced') -> float:
    """
    Calculate a quality score for a video based on various metrics.
    
    Args:
        video: Video data dictionary
        search_mode: One of 'recent', 'relevant', 'popular', or 'balanced'
        
    Returns:
        Float score where higher is better
    """
    # Base factors
    views = parse_view_count(video.get('views', '0'))
    duration = parse_duration(video.get('duration', '0:00'))
    age_hours = (datetime.now() - video.get('published_at', datetime.now())).total_seconds() / 3600
    
    # Channel quality indicators
    channel_indicators = {
        'finance': 2.0,
        'invest': 2.0,
        'stock': 2.0,
        'trading': 1.5,
        'money': 1.2,
        'business': 1.2,
        'news': 1.2,
    }
    
    # Title quality indicators
    title_indicators = {
        'analysis': 2.0,
        'prediction': 1.5,
        'forecast': 1.5,
        'technical': 1.3,
        'fundamental': 1.3,
        'earnings': 1.3,
        'research': 1.2,
        'review': 1.2,
    }
    
    # Calculate channel score
    channel_name = video.get('channel', '').lower()
    channel_score = sum(boost for word, boost in channel_indicators.items() if word in channel_name)
    channel_score = max(1.0, channel_score)  # Minimum score of 1.0
    
    # Calculate title score
    title = video.get('title', '').lower()
    title_score = sum(boost for word, boost in title_indicators.items() if word in title)
    title_score = max(1.0, title_score)  # Minimum score of 1.0
    
    # Penalize extremely short or long videos
    duration_penalty = 1.0
    if duration < 120:  # Less than 2 minutes
        duration_penalty = 0.5
    elif duration > 3600:  # More than 1 hour
        duration_penalty = 0.7
    
    # Calculate base score based on views and engagement
    view_score = min(1 + (views / 10000), 5.0)  # Cap at 5.0
    
    # Calculate recency score (exponential decay)
    recency_score = max(0.1, 1.0 * pow(0.99, age_hours))
    
    # Calculate final score based on search mode
    if search_mode == 'recent':
        final_score = (
            recency_score * 0.6 +
            title_score * 0.2 +
            channel_score * 0.1 +
            view_score * 0.1
        ) * duration_penalty
    elif search_mode == 'popular':
        final_score = (
            view_score * 0.6 +
            title_score * 0.2 +
            channel_score * 0.1 +
            recency_score * 0.1
        ) * duration_penalty
    elif search_mode == 'relevant':
        final_score = (
            title_score * 0.4 +
            channel_score * 0.3 +
            view_score * 0.2 +
            recency_score * 0.1
        ) * duration_penalty
    else:  # balanced
        final_score = (
            title_score * 0.3 +
            channel_score * 0.2 +
            view_score * 0.25 +
            recency_score * 0.25
        ) * duration_penalty
    
    return final_score

async def fetch_stock_videos(ticker: str, max_results: int = 5, search_mode: str = 'balanced') -> List[Dict[str, Any]]:
    """
    Fetch stock-related videos from YouTube using their AJAX API.
    
    Args:
        ticker: Stock ticker symbol
        max_results: Maximum number of videos to return
        search_mode: One of 'recent', 'relevant', 'popular', or 'balanced'
        
    Returns:
        List of video information dictionaries
    """
    logger.info(f"Fetching YouTube videos for ticker: {ticker} (mode: {search_mode})")
    
    # Construct search URL and parameters for AJAX endpoint
    url = "https://www.youtube.com/youtubei/v1/search"
    params = {
        "key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",  # Public client-side API key
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-YouTube-Client-Name": "1",
        "X-YouTube-Client-Version": "2.20240215.01.00",
    }
    
    # Adjust search parameters based on mode
    sort_param = {
        'recent': 'CAISAhAB',  # Upload date
        'popular': 'CAMSAhAB',  # View count
        'relevant': 'CAASAhAB',  # Relevance
        'balanced': 'CAASAhAB',  # Relevance
    }.get(search_mode, 'CAASAhAB')
    
    # Construct request payload
    payload = {
        "context": {
            "client": {
                "hl": "en",
                "gl": "US",
                "clientName": "WEB",
                "clientVersion": "2.20240215.01.00",
            }
        },
        "query": f"{ticker} stock analysis",
        "params": sort_param
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            logger.debug(f"Making request to {url}")
            async with session.post(url, params=params, headers=headers, json=payload) as response:
                if response.status != 200:
                    logger.error(f"YouTube request failed with status {response.status}")
                    return []
                
                try:
                    data = await response.json()
                    logger.debug("Successfully parsed YouTube data")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse YouTube data: {str(e)}")
                    return []
                
                videos = []
                try:
                    # Extract videos from the response
                    contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
                    
                    # Find video items
                    items = []
                    for section in contents:
                        if 'itemSectionRenderer' in section:
                            items = section['itemSectionRenderer'].get('contents', [])
                            break
                    
                    logger.debug(f"Found {len(items)} potential video items")
                    
                    # Collect all valid videos first
                    all_videos = []
                    for item in items:
                        video_renderer = item.get('videoRenderer')
                        if not video_renderer:
                            continue
                        
                        try:
                            # Extract video information with better error handling
                            video_id = video_renderer.get('videoId', '')
                            
                            # Title is nested in runs array
                            title_runs = video_renderer.get('title', {}).get('runs', [])
                            title = title_runs[0].get('text', '') if title_runs else ''
                            
                            # Description might be in different formats
                            description = ''
                            desc_snippet = video_renderer.get('descriptionSnippet', {})
                            if isinstance(desc_snippet, dict):
                                desc_runs = desc_snippet.get('runs', [])
                                description = ''.join(run.get('text', '') for run in desc_runs)
                            
                            # Channel name is nested
                            channel_runs = video_renderer.get('ownerText', {}).get('runs', [])
                            channel = channel_runs[0].get('text', '') if channel_runs else ''
                            
                            # Published date
                            published = video_renderer.get('publishedTimeText', {}).get('simpleText', '')
                            
                            # View count
                            views = video_renderer.get('viewCountText', {}).get('simpleText', '')
                            
                            # Duration
                            duration = video_renderer.get('lengthText', {}).get('simpleText', '')
                            
                            if not (video_id and title):  # Skip if missing essential info
                                continue
                            
                            video_data = {
                                "title": title,
                                "url": f"https://youtube.com/watch?v={video_id}",
                                "summary": description[:200] + "..." if description else "",
                                "channel": channel,
                                "views": views,
                                "duration": duration,
                                "published_at": parse_relative_time(published)
                            }
                            
                            # Calculate video score
                            video_data['score'] = calculate_video_score(video_data, search_mode)
                            all_videos.append(video_data)
                            logger.debug(f"Added video: {title} (score: {video_data['score']:.2f})")
                            
                        except Exception as e:
                            logger.warning(f"Error extracting video data: {str(e)}")
                            continue
                    
                    # Sort videos by score and take top N
                    videos = sorted(all_videos, key=lambda x: x['score'], reverse=True)[:max_results]
                    logger.info(f"Found {len(videos)} videos after scoring")
                    return videos
                    
                except Exception as e:
                    logger.error(f"Error parsing YouTube video data: {str(e)}")
                    logger.error(f"Stack trace: {traceback.format_exc()}")
                    return []
                    
    except aiohttp.ClientError as e:
        logger.error(f"Network error fetching YouTube videos: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching YouTube videos: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return []

if __name__ == "__main__":
    async def test():
        videos = await fetch_stock_videos("AAPL")
        for video in videos:
            print(f"\nTitle: {video['title']}")
            print(f"Channel: {video['channel']}")
            print(f"URL: {video['url']}")
            print(f"Summary: {video['summary']}")
            print(f"Views: {video['views']}")
            print(f"Duration: {video['duration']}")
            print(f"Published: {video['published_at']}")
            print(f"Score: {video['score']:.2f}")
            print("-" * 80)
    
    asyncio.run(test())