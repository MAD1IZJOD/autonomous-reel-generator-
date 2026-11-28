"""Media probing, rendering and QC helpers backed by FFmpeg/FFprobe."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, capture_output=True, text=True)


def probe(path: Path | str, ffprobe_bin: str = "ffprobe") -> dict[str, Any]:
    command = [
        ffprobe_bin,
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=index,codec_type,width,height,r_frame_rate,avg_frame_rate,nb_frames,sample_rate,channels",
        "-of",
        "json",
        str(path),
    ]
    result = _run(command)
    return json.loads(result.stdout)


def media_duration(path: Path | str, ffprobe_bin: str = "ffprobe") -> float:
    data = probe(path, ffprobe_bin)
    return float(data["format"]["duration"])


def frame_rate(path: Path | str, ffprobe_bin: str = "ffprobe") -> float:
    data = probe(path, ffprobe_bin)
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            for key in ("avg_frame_rate", "r_frame_rate"):
                rate = stream.get(key)
                if not rate or rate == "0/0":
                    continue
                numerator, denominator = rate.split("/")
                if float(denominator) == 0:
                    continue
                return float(numerator) / float(denominator)
    raise ValueError("no video stream found")


def frame_count(path: Path | str, ffprobe_bin: str = "ffprobe") -> int:
    data = probe(path, ffprobe_bin)
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            if "nb_frames" in stream:
                return int(stream["nb_frames"])
    # Fall back to counting packets if nb_frames is unavailable.
    command = [
        ffprobe_bin,
        "-v",
        "error",
        "-count_frames",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=nb_read_frames",
        "-of",
        "csv=p=0",
        str(path),
    ]
    result = _run(command)
    return int(result.stdout.strip().splitlines()[0])


def make_video_from_image(
    image_path: Path | str,
    output_path: Path | str,
    duration_s: float,
    width: int,
    height: int,
    fps: int = 25,
    ffmpeg_bin: str = "ffmpeg",
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            ffmpeg_bin,
            "-y",
            "-loop",
            "1",
            "-i",
            str(image_path),
            "-t",
            f"{duration_s:.3f}",
            "-r",
            str(fps),
            "-vf",
            f"scale={width}:{height},format=yuv420p",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(output),
        ]
    )
    return output


def concatenate_videos(
    video_paths: list[Path | str],
    output_path: Path | str,
    fps: int = 25,
    width: int = 1080,
    height: int = 1920,
    durations: list[float] | None = None,
    ffmpeg_bin: str = "ffmpeg",
) -> Path:
    """Concatenate clips onto an exact timeline.

    Each clip is scaled, padded, retimed and conformed to its planned duration so
    the visual track matches the voice-driven timeline instead of inheriting
    whatever length the provider happened to return.
    """
    if not video_paths:
        raise ValueError("no videos to concatenate")
    if durations is not None and len(durations) != len(video_paths):
        raise ValueError("durations must match the number of video paths")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [ffmpeg_bin, "-y"]
    for path in video_paths:
        command += ["-i", str(path)]

    chains = []
    concat_inputs = ""
    for index, _ in enumerate(video_paths):
        chain = (
            f"[{index}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}"
        )
        if durations is not None:
            duration = max(0.04, round(float(durations[index]), 3))
            chain += f",tpad=stop_mode=clone:stop_duration={duration:.3f},trim=duration={duration:.3f}"
        chain += f",setpts=PTS-STARTPTS[v{index}]"
        chains.append(chain)
        concat_inputs += f"[v{index}]"

    filter_complex = ";".join(chains) + f";{concat_inputs}concat=n={len(video_paths)}:v=1:a=0[v]"
    command += [
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-r",
        str(fps),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output),
    ]
    _run(command)
    return output


def mix_audio(
    voice_paths: list[Path | str],
    music_path: Path | str,
    output_path: Path | str,
    total_duration_s: float,
    sample_rate: int = 48000,
    target_lufs: float = -14.0,
    true_peak_db: float = -1.0,
    ffmpeg_bin: str = "ffmpeg",
) -> Path:
    if not voice_paths:
        raise ValueError("no voice tracks to mix")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [ffmpeg_bin, "-y"]
    for path in voice_paths:
        command += ["-i", str(path)]
    command += ["-stream_loop", "-1", "-i", str(music_path)]

    voice_concat = "".join(f"[{index}:a]" for index in range(len(voice_paths)))
    voice_index = len(voice_paths)
    filter_complex = (
        f"{voice_concat}concat=n={len(voice_paths)}:v=0:a=1[voice];"
        f"[voice]asplit=2[voice_out][sidechain];"
        f"[{voice_index}:a]volume=0.35[music];"
        f"[music][sidechain]sidechaincompress=threshold=0.03:ratio=8:attack=5:release=250[ducked];"
        f"[voice_out][ducked]amix=inputs=2:duration=first:normalize=0,"
        f"loudnorm=I={target_lufs}:TP={true_peak_db}:LRA=11[out]"
    )
    try:
        _run(
            command
            + [
                "-filter_complex",
                filter_complex,
                "-map",
                "[out]",
                "-t",
                f"{total_duration_s:.3f}",
                "-ar",
                str(sample_rate),
                "-ac",
                "2",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                str(output),
            ]
        )
    except subprocess.CalledProcessError:
        simple_filter = (
            f"{voice_concat}concat=n={len(voice_paths)}:v=0:a=1[voice];"
            f"[{voice_index}:a]volume=0.35[music];"
            f"[voice][music]amix=inputs=2:duration=first:normalize=0,"
            f"loudnorm=I={target_lufs}:TP={true_peak_db}:LRA=11[out]"
        )
        _run(
            command
            + [
                "-filter_complex",
                simple_filter,
                "-map",
                "[out]",
                "-t",
                f"{total_duration_s:.3f}",
                "-ar",
                str(sample_rate),
                "-ac",
                "2",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                str(output),
            ]
        )
    return output


def mux_audio_video(
    video_path: Path | str,
    audio_path: Path | str,
    output_path: Path | str,
    ffmpeg_bin: str = "ffmpeg",
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            ffmpeg_bin,
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(audio_path),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    return output


def qc_black_frames(path: Path | str, ffmpeg_bin: str = "ffmpeg") -> int:
    command = [
        ffmpeg_bin,
        "-i",
        str(path),
        "-vf",
        "blackdetect=d=0.1:pix_th=0.00",
        "-an",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return len(re.findall(r"black_start:", result.stderr))


def qc_frozen_frames(path: Path | str, ffmpeg_bin: str = "ffmpeg") -> int:
    command = [
        ffmpeg_bin,
        "-i",
        str(path),
        "-vf",
        "freezedetect=n=0.003:d=0.5",
        "-an",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return len(re.findall(r"freeze_start:", result.stderr))


def qc_loudness(path: Path | str, ffmpeg_bin: str = "ffmpeg") -> dict[str, float | None]:
    command = [ffmpeg_bin, "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"]
    result = subprocess.run(command, capture_output=True, text=True)
    text = result.stderr
    # ebur128 prints a running value before the final summary, so take the last match.
    loudness_matches = re.findall(r"I:\s*(-?\d+(?:\.\d+)?)\s*LUFS", text)
    peak_matches = re.findall(r"Peak:\s*(-?\d+(?:\.\d+)?)\s*dBFS", text)
    return {
        "integrated_lufs": float(loudness_matches[-1]) if loudness_matches else None,
        "true_peak_dbfs": float(peak_matches[-1]) if peak_matches else None,
    }


def contact_sheet(
    video_path: Path | str,
    output_path: Path | str,
    fps: float = 0.5,
    ffmpeg_bin: str = "ffmpeg",
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            ffmpeg_bin,
            "-y",
            "-i",
            str(video_path),
            "-vf",
            f"fps={fps},scale=270:480,tile=4x3",
            "-frames:v",
            "1",
            str(output),
        ]
    )
    return output
