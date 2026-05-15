#!/usr/bin/env python3
"""
Video Strategy Analyzer
Pipeline: YouTube URL → Audio → Whisper Transcript → Frames → Vision Analysis → Strategy Rules
"""
import os
import subprocess
import json
import urllib.request
from datetime import datetime, timezone

# ─── CONFIG ──────────────────────────────────────────────────────
YT_DLP = "/opt/data/bin/yt-dlp"
FFMPEG = "/usr/bin/ffmpeg"
DATA_DIR = "/opt/data/projects/trading-brain/data/videos"
STRATEGIES_DIR = "/opt/data/projects/trading-brain/strategies"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STRATEGIES_DIR, exist_ok=True)

def run_cmd(cmd, timeout=300):
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return result.returncode == 0, result.stdout, result.stderr

def download_video(url, output_dir):
    """Download YouTube video audio + video with yt-dlp"""
    print(f"  📥 Downloading: {url}")
    
    # Download best quality, extract audio
    cmd = f"{YT_DLP} -o '{output_dir}/%(title)s.%(ext)s' --write-info-json --write-thumbnail '{url}'"
    ok, out, err = run_cmd(cmd, timeout=180)
    
    if not ok:
        print(f"   ❌ Download failed: {err[:200]}")
        return None
    
    # Find downloaded files
    files = os.listdir(output_dir)
    video_file = None
    info_file = None
    
    for f in files:
        if f.endswith('.info.json'):
            info_file = os.path.join(output_dir, f)
        elif any(f.endswith(ext) for ext in ['.mp4', '.webm', '.mkv']):
            video_file = os.path.join(output_dir, f)
    
    if video_file:
        print(f"   ✅ Video: {os.path.basename(video_file)}")
    if info_file:
        print(f"   ✅ Info: {os.path.basename(info_file)}")
    
    return {"video": video_file, "info": info_file, "dir": output_dir}

def extract_audio(video_path, output_dir):
    """Extract audio as MP3 for Whisper"""
    print(f"  🎤 Extracting audio...")
    
    audio_path = os.path.join(output_dir, "audio.mp3")
    cmd = f"{FFMPEG} -i '{video_path}' -vn -ar 16000 -ac 1 -b:a 32k '{audio_path}' -y"
    ok, out, err = run_cmd(cmd, timeout=120)
    
    if ok and os.path.exists(audio_path):
        size = os.path.getsize(audio_path)
        print(f"   ✅ Audio: {audio_path} ({size//1024}KB)")
        return audio_path
    else:
        print(f"   ❌ Audio extraction failed")
        return None

def transcribe_whisper(audio_path):
    """Transcribe audio using OpenAI Whisper API"""
    print(f"  👄 Transcribing with Whisper API...")
    
    if not OPENAI_API_KEY:
        print("   ⚠️ No OPENAI_API_KEY set, skipping transcription")
        return None
    
    import urllib.request
    
    # Whisper API expects multipart form data - we'll use curl via subprocess
    cmd = [
        "curl", "-s", "https://api.openai.com/v1/audio/transcriptions",
        "-H", f"Authorization: Bearer {OPENAI_API_KEY}",
        "-H", "Content-Type: multipart/form-data",
        "-F", "model=whisper-1",
        "-F", "language=en",
        "-F", "response_format=json",
        "-F", f"file=@{audio_path}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            text = data.get("text", "")
            print(f"   ✅ Transcript: {len(text)} chars")
            return text
        else:
            print(f"   ❌ Whisper API error: {result.stderr[:200]}")
            return None
    except Exception as e:
        print(f"   ❌ Whisper error: {e}")
        return None

def extract_frames(video_path, output_dir, interval=30):
    """Extract frames every N seconds"""
    print(f"  🖼️ Extracting frames (every {interval}s)...")
    
    frames_dir = os.path.join(output_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    
    # Extract frames using ffmpeg
    cmd = f"{FFMPEG} -i '{video_path}' -vf 'fps=1/{interval}' -q:v 2 '{frames_dir}/frame_%04d.jpg' -y"
    ok, out, err = run_cmd(cmd, timeout=120)
    
    if ok:
        frames = sorted([f for f in os.listdir(frames_dir) if f.endswith('.jpg')])
        print(f"   ✅ {len(frames)} frames extracted")
        return [os.path.join(frames_dir, f) for f in frames]
    else:
        print(f"   ❌ Frame extraction failed")
        return []

def analyze_frame(frame_path, prompt="Describe this trading chart or interface. What indicators, patterns, or signals do you see?"):
    """Analyze a single frame using vision API"""
    # This will be called via the vision_analyze tool in the main script
    # For now, return placeholder
    return {"frame": frame_path, "analysis": "VISION_ANALYSIS_PLACEHOLDER"}

def extract_strategy_rules(transcript, frame_analyses):
    """Extract trading strategy rules from transcript + frame analyses"""
    print(f"  🧠 Extracting strategy rules...")
    
    # Build combined context
    context = f"""You are analyzing a trading strategy video. Extract concrete, actionable trading rules.

VIDEO TRANSCRIPT:
{transcript[:5000] if transcript else "No transcript available"}

VISUAL ANALYSIS:
{json.dumps(frame_analyses, indent=2)[:2000] if frame_analyses else "No visual analysis"}

Extract the following:
1. Strategy name and description
2. Entry rules (exact conditions)
3. Exit rules (take profit, stop loss)
4. Risk management rules
5. Indicators used and their settings
6. Timeframe and asset preferences
7. Any backtest results or performance claims mentioned

Format as a structured strategy document with clear, testable rules.
"""
    
    # For now, return a placeholder structure
    # In production, this would call an LLM API
    strategy = {
        "name": "Extracted Strategy",
        "source": "YouTube Video",
        "transcript_length": len(transcript) if transcript else 0,
        "frames_analyzed": len(frame_analyses),
        "rules": {
            "entry": ["Rule extraction requires LLM call"],
            "exit": ["Rule extraction requires LLM call"],
            "risk_management": ["Rule extraction requires LLM call"]
        },
        "raw_transcript": transcript[:10000] if transcript else "",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    print(f"   ✅ Strategy structure created")
    return strategy

def process_video(url, strategy_name=None):
    """Main pipeline: YouTube URL → Strategy Document"""
    print(f"\n🎬 Video Strategy Analyzer")
    print(f"   URL: {url}")
    
    # Create working directory
    video_id = strategy_name or f"video_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    work_dir = os.path.join(DATA_DIR, video_id)
    os.makedirs(work_dir, exist_ok=True)
    
    # Step 1: Download
    downloaded = download_video(url, work_dir)
    if not downloaded or not downloaded["video"]:
        print("❌ Download failed, aborting")
        return None
    
    video_path = downloaded["video"]
    
    # Step 2: Extract audio
    audio_path = extract_audio(video_path, work_dir)
    
    # Step 3: Transcribe
    transcript = None
    if audio_path:
        transcript = transcribe_whisper(audio_path)
    
    # Step 4: Extract frames
    frames = extract_frames(video_path, work_dir)
    
    # Step 5: Analyze frames (placeholder - would use vision API)
    frame_analyses = []
    for i, frame in enumerate(frames[:10]):  # Analyze first 10 frames
        print(f"   Frame {i+1}/{min(len(frames), 10)}: {os.path.basename(frame)}")
        # In production: vision_analyze(frame, "...")
        frame_analyses.append({"path": frame, "timestamp_sec": i * 30})
    
    # Step 6: Extract strategy
    strategy = extract_strategy_rules(transcript, frame_analyses)
    strategy["video_url"] = url
    strategy["video_path"] = video_path
    strategy["work_dir"] = work_dir
    
    # Save strategy
    if strategy_name:
        strategy["name"] = strategy_name
    
    output_file = os.path.join(STRATEGIES_DIR, f"{video_id}.json")
    with open(output_file, 'w') as f:
        json.dump(strategy, f, indent=2)
    
    print(f"\n  💾 Strategy saved: {output_file}")
    print(f"  📝 Transcript: {len(transcript) if transcript else 0} chars")
    print(f"  🖼️ Frames: {len(frames)}")
    print(f"  📁 Work dir: {work_dir}")
    
    return strategy

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 video_analyzer.py <youtube_url> [strategy_name]")
        print("Example: python3 video_analyzer.py 'https://youtube.com/watch?v=...' 'EMA_Cross_Strategy'")
        sys.exit(1)
    
    url = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = process_video(url, name)
        if result:
            print(f"\n✅ Video analysis complete!")
        else:
            print(f"\n❌ Analysis failed")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
