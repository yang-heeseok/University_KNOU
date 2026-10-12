# Source adoption assessment — Systran/faster-whisper-small

**Status:** Recorded. This comparison does not itself authorize a model dependency.

## What this record does not own

| Question | Owner |
| --- | --- |
| Transcript behavior and usage | `scripts/knou_transcribe.py`, `scripts/download-knou.README.md` |
| Model revision selected for runtime | `MODEL_REPO` and `MODEL_REVISION` in `scripts/knou_transcribe.py` |

## 1. Source and scope

**Source type:** Released model weights. **Target:** Hugging Face repository `Systran/faster-whisper-small` revision `536b0662742c02347bc0e980a01041f333bce120`, resolved from the model API `https://huggingface.co/api/models/Systran/faster-whisper-small` on 2026-10-10. The command printed the API's `sha` and `cardData.license`; the revision is passed to `snapshot_download` at runtime.

**Licence observed:** MIT in the model repository's card metadata. **In scope:** Repository revision, declared licence, model files needed by faster-whisper. **Out of scope:** Training data, model evaluation, accuracy on KNOU lectures, and alternative model sizes.

## 2. Observed shape

The `small` multilingual model can be loaded by `WhisperModel` on CPU with int8 computation. The first use downloads weights into the Hugging Face cache; subsequent use reads the cached revision. Korean is set as the default transcription language.

## 3. Candidate comparison

| Candidate | What this project has | Route | Grounds |
| --- | --- | --- | --- |
| Pinned multilingual small model | No locally cached KNOU-specific speech model | Direct adoption | A fixed revision gives reproducible model selection and supports Korean. The model is only fetched when the user invokes transcription. |

## 4. Evidence and limits

The model repository API returned the revision and MIT licence. `scripts/knou_transcribe.py` names that exact revision. The 483 MB weight file downloaded, loaded on CPU, and transcribed a local silence sample through the TXT/SRT path. A real KNOU lecture has not been transcribed, so output quality and runtime on a full lecture are unknown.

## 5. Result and reconsideration condition

Direct adoption is implemented as an optional runtime model. No general source-adoption rule was earned. Reconsider size or revision if Korean lecture accuracy or CPU runtime is unsatisfactory in a real sample.
