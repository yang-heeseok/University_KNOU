# Source adoption assessment — faster-whisper 1.2.1

**Status:** Recorded. This comparison does not itself authorize a dependency.

## What this record does not own

| Question | Owner |
| --- | --- |
| Transcript behavior and usage | `scripts/knou_transcribe.py`, `scripts/download-knou.README.md` |
| Dependency declaration | `scripts/requirements-transcribe.txt` |
| Implementation result | Code diff and local verification |

## 1. Source and scope

**Source type:** PyPI package. **Target:** `faster-whisper` 1.2.1 wheel `faster_whisper-1.2.1-py3-none-any.whl`, SHA-256 `79a66ad50688c0b794dd501dc340a736992a6342f7f95e5811be60b5224a26a7`. Resolved on 2026-10-10 from PyPI version metadata with `https://pypi.org/pypi/faster-whisper/1.2.1/json` and `python -m pip install --dry-run faster-whisper==1.2.1`.

**Licence observed:** MIT in PyPI metadata and [upstream LICENSE](https://github.com/SYSTRAN/faster-whisper/blob/master/LICENSE). **In scope:** [transcription API and CPU int8 usage](https://github.com/SYSTRAN/faster-whisper), package dependencies, local installation. **Out of scope:** Full wheel review, upstream benchmark claims, model weights (assessed separately), and real KNOU lecture accuracy.

## 2. Observed shape

The package supplies `WhisperModel` for local speech transcription. It depends on `ctranslate2`, `huggingface-hub`, `tokenizers`, `onnxruntime`, `av`, and `tqdm`. `av` decodes the MP4 audio; the existing download script already depends on FFmpeg for saving.

## 3. Candidate comparison

| Candidate | What this project has | Route | Grounds |
| --- | --- | --- | --- |
| Local CPU transcription | No speech-to-text implementation; existing `torch`/`transformers` are not wired to this CLI | Direct adoption | The user requested transcripts from downloaded lectures. An optional package and flag avoid slowing ordinary downloads. |

## 4. Evidence and limits

`python -m pip install faster-whisper==1.2.1` succeeded on this Windows/Python 3.13 machine. The pinned model loaded on CPU and a local silence file passed through the transcription path, producing TXT/SRT. A mocked speech segment checked text, timestamps, and existing-file refusal. The user requested the new behavior. `scripts/download-knou.README.md` owns usage and `scripts/requirements-transcribe.txt` pins the direct dependency. Accuracy on a real Korean lecture remains unverified.

## 5. Result and reconsideration condition

Direct adoption is implemented as an optional dependency. No general source-adoption rule was earned. Reconsider if a local transcription tool already installed by the user supplies a better supported API.
