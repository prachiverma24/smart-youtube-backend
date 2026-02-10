import sys
import json
from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id):
    try:
        # Try new API style (instantiation)
        # Check if static method exists
        if hasattr(YouTubeTranscriptApi, 'get_transcript'):
             transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        else:
             # Fallback to instance method 'fetch' or 'get_transcript'
             api = YouTubeTranscriptApi()
             if hasattr(api, 'get_transcript'):
                 transcript_list = api.get_transcript(video_id)
             elif hasattr(api, 'fetch'):
                 transcript_list = api.fetch(video_id)
             else:
                 return json.dumps({"success": False, "error": "No suitable method found in YouTubeTranscriptApi"})
        
        # Combine text
        full_text = ""
        if transcript_list:
            parts = []
            for item in transcript_list:
                if isinstance(item, dict):
                    parts.append(item.get('text', ''))
                elif hasattr(item, 'text'):
                    parts.append(item.text)
                else:
                    parts.append(str(item))
            full_text = " ".join(parts)
        
        return json.dumps({"success": True, "transcript": full_text})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No video ID provided"}))
        sys.exit(1)
        
    video_id = sys.argv[1]
    print(get_transcript(video_id))