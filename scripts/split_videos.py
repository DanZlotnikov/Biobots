import subprocess
import math

VIDEO = "fish.mp4"
NUM_PARTS = 10

def get_duration(video_path):
    """Return video duration in seconds (float) using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return float(result.stdout.strip())


def split_video(video_path, num_parts):
    duration = get_duration(video_path)
    chunk = duration / num_parts

    print(f"Total duration: {duration:.3f} sec")
    print(f"Each chunk: {chunk:.3f} sec")

    for i in range(num_parts):
        start = i * chunk
        start_str = f"{start:.3f}"       # ensures valid ffmpeg timestamp
        chunk_str = f"{chunk:.3f}"

        output = f"part_{i}.mp4"
        print(f"Creating {output} starting at {start_str}s")

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss", start_str,
                "-i", video_path,
                "-t", chunk_str,
                "-c", "copy",
                output
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    print("Done!")


# Run it
split_video(VIDEO, NUM_PARTS)
