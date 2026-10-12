"""Transcribe a downloaded lecture to UTF-8 text and SRT subtitles."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


MODEL_REPO = "Systran/faster-whisper-small"
MODEL_REVISION = "536b0662742c02347bc0e980a01041f333bce120"


def srt_time(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def transcribe(video: Path, language: str = "ko") -> tuple[Path, Path]:
    video = video.resolve()
    if not video.is_file():
        raise FileNotFoundError(f"영상 파일을 찾을 수 없습니다: {video}")
    text_path = video.with_suffix(".txt")
    srt_path = video.with_suffix(".srt")
    for path in (text_path, srt_path):
        if path.exists():
            raise FileExistsError(f"전사 파일이 이미 있습니다: {path}")

    try:
        from faster_whisper import WhisperModel
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError(
            "전사 패키지가 없습니다. python -m pip install -r scripts\\requirements-transcribe.txt"
        ) from exc

    print("전사 모델 캐시를 확인합니다. 없으면 다운로드합니다.", flush=True)
    model_dir = snapshot_download(repo_id=MODEL_REPO, revision=MODEL_REVISION)
    print(f"전사 모델 위치: {model_dir}", flush=True)
    model = WhisperModel(model_dir, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(
        str(video), language=language, beam_size=5,
        condition_on_previous_text=False, vad_filter=True,
    )

    text_part = text_path.with_name(text_path.name + ".part")
    srt_part = srt_path.with_name(srt_path.name + ".part")
    for path in (text_part, srt_part):
        if path.exists():
            raise FileExistsError(f"이전 임시 전사 파일이 있습니다: {path}")

    try:
        text_created = False
        with text_part.open("x", encoding="utf-8", newline="\n") as text_file, \
                srt_part.open("x", encoding="utf-8", newline="\n") as srt_file:
            count = 0
            for segment in segments:
                sentence = segment.text.strip()
                if not sentence:
                    continue
                count += 1
                text_file.write(sentence + "\n")
                srt_file.write(
                    f"{count}\n{srt_time(segment.start)} --> {srt_time(segment.end)}\n"
                    f"{sentence}\n\n"
                )
                print(f"\r전사 중: {srt_time(segment.end)}", end="", flush=True)
        print()
        text_part.rename(text_path)
        text_created = True
        srt_part.rename(srt_path)
    except BaseException:
        text_part.unlink(missing_ok=True)
        srt_part.unlink(missing_ok=True)
        if text_created:
            text_path.unlink(missing_ok=True)
        raise
    print(f"텍스트 저장: {text_path}")
    print(f"자막 저장: {srt_path}")
    return text_path, srt_path


def main() -> int:
    parser = argparse.ArgumentParser(description="다운로드한 KNOU MP4를 텍스트와 SRT로 전사합니다.")
    parser.add_argument("video", type=Path, help="전사할 MP4 파일")
    parser.add_argument("--language", default="ko", help="음성 언어 코드 (기본값: ko)")
    args = parser.parse_args()
    transcribe(args.video, args.language)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, OSError, RuntimeError, ValueError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
