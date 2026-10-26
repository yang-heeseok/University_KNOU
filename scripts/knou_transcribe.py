"""Transcribe a lecture, call or interview recording to UTF-8 text and SRT subtitles."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


# Pinned revisions keep results reproducible; the cache is reused offline.
MODELS = {
    "large-v3": ("Systran/faster-whisper-large-v3", "edaa852ec7e145841d8ffdb056a99866b5f0a478"),
    "large-v3-turbo": ("mobiuslabsgmbh/faster-whisper-large-v3-turbo", "0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf"),
    "small": ("Systran/faster-whisper-small", "536b0662742c02347bc0e980a01041f333bce120"),
}
DEFAULT_MODEL = "large-v3"
DIARIZATION = ("pyannote/speaker-diarization-community-1", "3533c8cf8e369892e6b79ff1bf80f7b0286a54ee")
SAMPLE_RATE = 16_000


def srt_time(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def model_snapshot(repo: str, revision: str) -> str:
    """Use the cached snapshot first so a blocked network does not stop local transcription."""
    from huggingface_hub import snapshot_download
    from huggingface_hub.errors import LocalEntryNotFoundError

    try:
        return snapshot_download(repo_id=repo, revision=revision, local_files_only=True)
    except LocalEntryNotFoundError:
        print(f"캐시에 없어 다운로드합니다: {repo}", flush=True)
        return snapshot_download(repo_id=repo, revision=revision)


def speaker_turns(audio, speakers: int | None):
    """Return (start, end, speaker) turns without overlaps, labelled 화자 1, 화자 2, ..."""
    # Usage metrics are opt-out in pyannote 4; recordings stay on this PC.
    os.environ["PYANNOTE_METRICS_ENABLED"] = "false"
    try:
        import torch
        from pyannote.audio import Pipeline
        from pyannote.audio.telemetry import set_telemetry_metrics
    except ImportError as exc:
        raise RuntimeError(
            "화자 분리 패키지가 없습니다. python -m pip install -r scripts\\requirements-transcribe.txt"
        ) from exc
    set_telemetry_metrics(False)

    print("화자 분리 모델을 불러옵니다.", flush=True)
    pipeline = Pipeline.from_pretrained(model_snapshot(*DIARIZATION))
    output = pipeline({"waveform": torch.from_numpy(audio)[None], "sample_rate": SAMPLE_RATE},
                      num_speakers=speakers)
    # Exclusive turns never overlap, so each word maps to exactly one speaker.
    annotation = output.exclusive_speaker_diarization
    names = {label: f"화자 {index}" for index, label in enumerate(annotation.labels(), 1)}
    return [(turn.start, turn.end, names[label])
            for turn, _, label in annotation.itertracks(yield_label=True)]


def speaker_at(turns, start: float, end: float) -> str:
    middle = (start + end) / 2
    for turn_start, turn_end, name in turns:
        if turn_start <= middle <= turn_end:
            return name
    # A word between turns belongs to the nearest one.
    return min(turns, key=lambda turn: min(abs(turn[0] - middle), abs(turn[1] - middle)))[2] if turns else "화자 ?"


def utterances(segments, turns):
    """Yield (start, end, text); with turns, regroup words so each line has one speaker."""
    if turns is None:
        for segment in segments:
            sentence = segment.text.strip()
            if sentence:
                yield segment.start, segment.end, sentence
        return
    current = None
    for segment in segments:
        for word in segment.words or []:
            name = speaker_at(turns, word.start, word.end)
            if current and current[2] == name:
                current[1] = word.end
                current[3].append(word.word)
            else:
                if current:
                    yield current[0], current[1], f"{current[2]}: {''.join(current[3]).strip()}"
                current = [word.start, word.end, name, [word.word]]
    if current:
        yield current[0], current[1], f"{current[2]}: {''.join(current[3]).strip()}"


def transcribe(media: Path, language: str = "ko", model: str = DEFAULT_MODEL,
               diarize: bool = False, speakers: int | None = None) -> tuple[Path, Path]:
    media = media.resolve()
    if not media.is_file():
        raise FileNotFoundError(f"음성·영상 파일을 찾을 수 없습니다: {media}")
    if model not in MODELS:
        raise ValueError(f"모델은 {', '.join(MODELS)} 중 하나여야 합니다: {model}")
    text_path = media.with_suffix(".txt")
    srt_path = media.with_suffix(".srt")
    for path in (text_path, srt_path):
        if path.exists():
            raise FileExistsError(f"전사 파일이 이미 있습니다: {path}")

    try:
        from faster_whisper import WhisperModel, decode_audio
    except ImportError as exc:
        raise RuntimeError(
            "전사 패키지가 없습니다. python -m pip install -r scripts\\requirements-transcribe.txt"
        ) from exc

    print(f"전사 모델({model}) 캐시를 확인합니다. 없으면 다운로드합니다.", flush=True)
    model_dir = model_snapshot(*MODELS[model])
    print(f"전사 모델 위치: {model_dir}", flush=True)
    # Decode once and share the waveform with diarization.
    audio = decode_audio(str(media), sampling_rate=SAMPLE_RATE)
    turns = speaker_turns(audio, speakers) if diarize else None
    whisper = WhisperModel(model_dir, device="cpu", compute_type="int8")
    segments, _ = whisper.transcribe(
        audio, language=language, beam_size=5,
        condition_on_previous_text=False, vad_filter=True,
        word_timestamps=diarize,
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
            for count, (start, end, sentence) in enumerate(utterances(segments, turns), 1):
                text_file.write(sentence + "\n")
                srt_file.write(f"{count}\n{srt_time(start)} --> {srt_time(end)}\n{sentence}\n\n")
                print(f"\r전사 중: {srt_time(end)}", end="", flush=True)
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
    parser = argparse.ArgumentParser(description="강의 영상·통화·인터뷰 녹음을 텍스트와 SRT로 전사합니다.")
    parser.add_argument("media", type=Path, help="전사할 음성·영상 파일 (MP4, M4A, MP3, WAV 등)")
    parser.add_argument("--language", default="ko", help="음성 언어 코드 (기본값: ko)")
    parser.add_argument("--model", choices=list(MODELS), default=DEFAULT_MODEL,
                        help=f"전사 모델 (기본값: {DEFAULT_MODEL} — 정확도 우선, 빠르게는 large-v3-turbo · small)")
    parser.add_argument("--diarize", action="store_true", help="화자를 나눠 '화자 1:' 처럼 표시")
    parser.add_argument("--speakers", type=int, help="화자 수를 알면 지정 (예: 통화 2)")
    args = parser.parse_args()
    if args.speakers is not None and (args.speakers < 1 or not args.diarize):
        parser.error("--speakers 는 --diarize 와 함께 1 이상으로 지정합니다")
    transcribe(args.media, args.language, args.model, args.diarize, args.speakers)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, OSError, RuntimeError, ValueError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
