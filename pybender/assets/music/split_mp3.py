import os
import argparse
import librosa
import soundfile as sf

def split_mp3s(
    input_dir: str,
    output_dir: str,
    chunk_seconds: int = 30,
    min_last_chunk_seconds: int = 10,
    fade_ms: int = 500
):
    os.makedirs(output_dir, exist_ok=True)

    chunk_samples = chunk_seconds * 22050  # 22050 Hz sample rate
    min_last_chunk_samples = min_last_chunk_seconds * 22050

    files = sorted(
        f for f in os.listdir(input_dir) if f.lower().endswith(".mp3")
    )
    print(f"🎵 Found {len(files)} MP3 files in '{input_dir}'")
    if not files:
        print("❌ No MP3 files found.")
        return

    clip_counter = 1  # GLOBAL counter across all files

    for filename in files:
        input_path = os.path.join(input_dir, filename)
        
        # Load audio using librosa
        audio, sr = librosa.load(input_path, sr=22050, mono=True)
        
        total_samples = len(audio)
        total_duration = total_samples / sr

        print(f"\n🎧 Processing: {filename}")
        print(f"   Duration: {total_duration:.2f}s")

        for start_sample in range(0, total_samples, chunk_samples):
            end_sample = min(start_sample + chunk_samples, total_samples)
            chunk = audio[start_sample:end_sample]

            # Skip very short tail clips
            if len(chunk) < min_last_chunk_samples:
                print(
                    f"   ⏭️  Skipping last short clip ({len(chunk)/sr:.2f}s)"
                )
                break

            # Optional fade (simple linear fade)
            if fade_ms > 0:
                fade_samples = int((fade_ms / 1000) * sr)
                if fade_samples > 0 and len(chunk) > fade_samples * 2:
                    # Fade in
                    chunk[:fade_samples] *= (
                        [i / fade_samples for i in range(fade_samples)]
                    )
                    # Fade out
                    chunk[-fade_samples:] *= (
                        [i / fade_samples for i in range(fade_samples, 0, -1)]
                    )

            output_filename = f"audio_clip_{clip_counter}.mp3"
            output_path = os.path.join(output_dir, output_filename)

            # Export using soundfile (saves as WAV, then convert)
            # For MP3, we'll use a simple approach: save as WAV which soundfile supports natively
            sf.write(output_path.replace('.mp3', '.wav'), chunk, sr)
            
            # If you need MP3 specifically, use this instead:
            # librosa.output.write_wav(output_path.replace('.mp3', '.wav'), chunk, sr)

            print(f"   ✅ Saved: {output_filename.replace('.mp3', '.wav')}")

            clip_counter += 1

    print(f"\n🎉 Done. Total clips created: {clip_counter - 1}")


if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    input = script_dir
    output = os.path.join(script_dir, "audio_clips")
    split_mp3s(
        input_dir=input,
        output_dir=output,
        chunk_seconds=30,
        min_last_chunk_seconds=25,
        fade_ms=500
    )
