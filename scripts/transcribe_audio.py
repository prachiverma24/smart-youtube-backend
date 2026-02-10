import sys
import json
import whisper
import os

def transcribe_audio(audio_path):
    try:
        # Load the model
        # using 'tiny' model for faster CPU inference (was 'base')
        # device='cpu' explicitly since we installed cpu version of torch
        model = whisper.load_model("tiny", device="cpu")
        
        # Transcribe
        result = model.transcribe(audio_path)
        
        # Format output to match youtube-transcript-api format
        # [{ 'text': '...', 'start': 0.0, 'duration': 1.0 }]
        formatted_transcript = []
        for segment in result["segments"]:
            formatted_transcript.append({
                "text": segment["text"].strip(),
                "start": segment["start"],
                "duration": segment["end"] - segment["start"]
            })
            
        return formatted_transcript

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Audio file path required"}))
        sys.exit(1)
        
    audio_path = sys.argv[1]
    
    if not os.path.exists(audio_path):
        print(json.dumps({"error": f"File not found: {audio_path}"}))
        sys.exit(1)
        
    transcript = transcribe_audio(audio_path)
    print(json.dumps(transcript))
