import os
import re
import json
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

try:
    import openai
except Exception:
    openai = None


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from a URL or return the input if it already looks like an id."""
    if not url:
        return ""
    # Common patterns: youtu.be/<id>, youtube.com/watch?v=<id>, youtube.com/shorts/<id>
    patterns = [
        r"youtu\.be/([\w-]{11})",
        r"v=([\w-]{11})",
        r"/shorts/([\w-]{11})",
        r"/embed/([\w-]{11})",
        r"^([\w-]{11})$",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    # fallback: try to parse last path segment
    parts = url.rstrip("/\n ").split("/")
    if parts:
        candidate = parts[-1]
        if len(candidate) == 11:
            return candidate
    return ""


def get_transcript_text(video_id: str) -> str:
    """Fetch transcript text for the given video id using youtube-transcript-api."""
    if not video_id:
        raise ValueError("No video id provided")
    try:
        # newer versions of youtube-transcript-api expose an API class with instance methods
        # use the instance .fetch(...) which returns a FetchedTranscript
        fetched = YouTubeTranscriptApi().fetch(video_id)
        # convert to raw data (list of dicts with 'text')
        raw = fetched.to_raw_data()
        texts = [e.get("text", "") for e in raw]
        return "\n".join(texts)
    except TranscriptsDisabled:
        raise RuntimeError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise RuntimeError("No transcript found for this video.")
    except VideoUnavailable:
        raise RuntimeError("Video is unavailable.")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch transcript: {e}")


def call_openai_for_notes(transcript: str, api_key: str | None = None) -> dict:
    """Send transcript to OpenAI (ChatCompletion) and request JSON result with summary, key_points, quiz (10 questions).
    If `api_key` is provided it will be used, otherwise the function reads OPENAI_API_KEY from the environment.
    """
    # prefer explicit api_key (from UI) for ease of local testing
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set. Set it to your OpenAI API key or provide it in the UI.")
    if openai is None:
        raise RuntimeError("openai python package not installed.")

    openai.api_key = key

    system_msg = (
        "You are an assistant that converts a video transcript into a learning package. "
        "Return ONLY valid JSON with keys: summary (string), key_points (list of short strings), quiz (list of EXACTLY 10 strings). "
        "Do not include any extra commentary outside the JSON. Keep summary short (2-4 sentences)."
    )

    user_msg = (
        "Here is the transcript:\n\n" + transcript + "\n\n" +
        "From this transcript:\n" +
        "1) Create a short summary (2-4 sentences).\n" +
        "2) Give important key points as a bulleted list (concise).\n" +
        "3) Generate exactly 10 quiz questions (clear, varied difficulty).\n" +
        "Return the result as JSON exactly like: {\n  \"summary\": \"...\",\n  \"key_points\": [\"...\", ...],\n  \"quiz\": [\"Q1\", \"Q2\", ...]\n}\n"
    )

    try:
        # Support both pre-1.0 `openai` usage and the newer 1.0+ client
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        if hasattr(openai, "OpenAI"):
            # Newer OpenAI client (openai>=1.0.0)
            try:
                client = openai.OpenAI(api_key=key)
            except TypeError:
                # some versions expect API key from env / openai.api_key
                openai.api_key = key
                client = openai.OpenAI()

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.2,
                max_tokens=1200,
            )
        else:
            # Older interface
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.2,
                max_tokens=1200,
            )
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {e}")

    # Extract text from response in a resilient way
    def _extract_text(resp):
        # try attribute access first
        try:
            return resp.choices[0].message.content
        except Exception:
            pass
        try:
            return resp["choices"][0]["message"]["content"]
        except Exception:
            pass
        try:
            return resp.choices[0].text
        except Exception:
            pass
        # fallback to string
        return str(resp)

    text = _extract_text(response).strip()

    # Try direct JSON parse, otherwise try to extract JSON substring
    try:
        return json.loads(text)
    except Exception:
        # attempt to find first { ... } block
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                raise RuntimeError("OpenAI returned non-JSON output and automatic parsing failed.\nOutput:\n" + text)
        else:
            raise RuntimeError("OpenAI returned non-JSON output and no JSON object found.\nOutput:\n" + text)


# Streamlit UI
st.set_page_config(page_title="Smart Video Learning Tool", layout="wide")
st.title("Smart Video Learning Tool — YouTube → Notes + Quiz")
st.write("Paste a YouTube link and get a short summary, key points, and exactly 10 quiz questions.")

col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("YouTube link (or video id)")
with col2:
    model_choice = st.selectbox("OpenAI model", options=["gpt-3.5-turbo", "gpt-4"], index=0)
    # optional API key input for quick local testing (keeps key out of logs/UI unless entered)
    st.text_input("OpenAI API key (optional)", type="password", key="ui_openai_key")
    st.caption("Set OPENAI_API_KEY env var before running or paste a key above for this session.")
    # show whether an API key is available
    env_key = os.getenv("OPENAI_API_KEY")
    ui_key = st.session_state.get("ui_openai_key") if "ui_openai_key" in st.session_state else None
    if env_key:
        st.success("Using OpenAI key from environment (OPENAI_API_KEY).")
    elif ui_key:
        st.success("Using OpenAI key provided in this session.")
    else:
        st.warning("No OpenAI API key found. Paste one above or set OPENAI_API_KEY in the shell before starting the app.")

if st.button("Process"):
    if not url:
        st.error("Please paste a YouTube URL or video id.")
    else:
        with st.spinner("Extracting video id..."):
            vid = extract_video_id(url)
        if not vid:
            st.error("Could not extract a YouTube video id from the URL. Please check the link.")
        else:
            st.info(f"Video id: {vid}")
            try:
                with st.spinner("Fetching transcript..."):
                    transcript_text = get_transcript_text(vid)
                if not transcript_text.strip():
                    st.error("Transcript is empty.")
                else:
                    # show a trimmed preview and length
                    st.success("Transcript fetched.")
                    st.write(f"Transcript length: {len(transcript_text)} characters")
                    # confirm large transcripts
                    if len(transcript_text) > 15000:
                        st.warning("Transcript is large; API calls may be truncated. Consider using a shorter video or summarizing in parts.")

                    # call OpenAI
                    try:
                        os.environ["OPENAI_MODEL"] = model_choice
                        # prefer UI-provided API key if present
                        ui_api_key = st.session_state.get("ui_openai_key", None)
                        with st.spinner("Sending transcript to the AI and generating notes..."):
                            result = call_openai_for_notes(transcript_text, api_key=ui_api_key)

                        # Validate result keys
                        summary = result.get("summary", "")
                        key_points = result.get("key_points", [])
                        quiz = result.get("quiz", [])

                        st.markdown("---")
                        st.subheader("Summary")
                        st.write(summary)

                        st.subheader("Key Points")
                        if isinstance(key_points, list) and key_points:
                            for kp in key_points:
                                st.write(f"• {kp}")
                        else:
                            st.write("(No key points returned)")

                        st.subheader("Quiz — 10 Questions")
                        if isinstance(quiz, list) and len(quiz) == 10:
                            for i, q in enumerate(quiz, start=1):
                                st.write(f"{i}. {q}")
                        else:
                            st.warning("Quiz did not contain exactly 10 questions; showing what was returned.")
                            if isinstance(quiz, list):
                                for i, q in enumerate(quiz, start=1):
                                    st.write(f"{i}. {q}")
                            else:
                                st.write(quiz)

                    except Exception as e:
                        st.error(f"Failed to generate notes: {e}")

            except Exception as ex:
                st.error(f"Could not fetch transcript: {ex}")
