# Talker — Local Speech Toolkit

Overview
--------
Talker is a small local speech toolkit that captures microphone audio, applies a band-pass filter, transcribes speech with Vosk, and can synthesize/play back audio (TTS). The repository contains glue code, utilities, and sample models for experimenting with STT/TTS pipelines.

Quick facts
- STT backend: Vosk (models located in `models/`)
- Audio I/O: `sounddevice`
- Filtering: `scipy.signal` Butterworth band-pass implemented in `speech_manager/audio_filter.py`
- Logging utilities in `src/utils/logger.py`
- Small demo documents in `documents/`

Prerequisites
-------------
- Python 3.10+ recommended (project contains pycache for 3.10/3.11)
- On Windows: ensure microphone drivers and `sounddevice` dependencies are available
- Install Python deps:
  - Open PowerShell/CMD in repo root:
    - pip install -r src/requirements.txt

Project structure
-----------------
c:\_c_github\talker/
- README.md (this file)
- documents/
  - little_red_hen.txt
- models/
  - vosk-model-.../  (Vosk acoustic/language models; large binaries)
- other/
  - config.py, main.py, test_stt.py, rag_core.py, schemas.py (aux scripts / experiments)
- src/
  - main.py (project entrypoint in `src/`)
  - requirements.txt
  - cache/
    - cache_manager.py
  - core/
    - text_processing.py
  - document_manager/
    - document_manager.py (placeholder / docs added)
  - logs/
    - app.log
  - speech_manager/
    - audio_filter.py  — band-pass filter + AudioFilterConfig (Pydantic)
    - audio_input.py   — audio capture, Vosk recognizer, debug FFT helper
    - audio_output.py  — TTS / playback logic
    - readme.md
  - utils/
    - logger.py  — logging setup (attach handlers, levels)
    - tts.py / test_tts.py

Key modules and responsibilities
--------------------------------
- speech_manager/audio_input.py
  - Captures microphone audio via `sounddevice`, queues buffers, runs Vosk recognizer.
  - Contains `log_dominant_frequency` helper for FFT-based diagnostics.
  - Instantiate `SpeechToText(model_path, device_id, filter_config)` for STT.

- speech_manager/audio_filter.py
  - `AudioFilterConfig` (Pydantic) validates cutoff frequencies and order.
  - `AudioFilter` designs a Butterworth band-pass and applies it using `filtfilt`.
  - Note: `Field(..., ge=20.0)` means lower cutoff must be >= 20 Hz.

- speech_manager/audio_output.py & utils/tts.py
  - TTS synthesis and playback. Reuse a single TTS engine instance across calls (avoid re-initializing inside loops).

- utils/logger.py
  - Central place to attach handlers and configure levels. Set to DEBUG to enable `log_dominant_frequency` messages.

Workflow (typical)
------------------
1. Start the application (see `src/main.py` or `other/test_stt.py`).
2. Audio captured from microphone via `sounddevice` stream in `audio_input`.
3. Raw audio chunk optionally logged (dominant frequency) for diagnostics.
4. Audio chunk passed through `AudioFilter.process(...)` to reduce out-of-band noise.
5. Filtered audio fed into Vosk `KaldiRecognizer` → partial/final JSON results → extracted text.
6. Text routed to business logic / document manager / TTS.
7. TTS engine (from `utils/tts.py` / `audio_output.py`) synthesizes audio and plays it back.

How to run (example)
--------------------
1. Install deps:
   - pip install -r src/requirements.txt
2. Choose a Vosk model folder under `models/` (e.g. `models/vosk-model-small-en-us-0.15`).
3. Run a simple STT demo (example patterns):
   - python -m src.main
   - or edit `other/test_stt.py` to point to the desired model and run it:
     - python other/test_stt.py
4. If no audio is heard from TTS after first utterance, ensure the TTS engine is instantiated once and not recreated per loop (see `utils/tts.py`).

Debugging and logging
---------------------
- Set logger to DEBUG in `src/utils/logger.py` to see:
  - FFT dominant frequency diagnostics from `log_dominant_frequency`.
  - Filter design messages from `AudioFilter`.
  - Vosk initialization and recognition lifecycle logs.
- Check `src/logs/app.log` for persisted logs (if configured).
- If STT works once and then fails:
  - Confirm TTS engine reuse (do not recreate per iteration).
  - Inspect exceptions in logs (wrap TTS calls with try/except and log exc_info=True).

Documentation status & recommendations
--------------------------------------
- Many modules have basic docstrings (good). Recommended next steps:
  - Add module-level docstrings to every file that lacks one (e.g., `document_manager/document_manager.py` is a placeholder — expanded).
  - Add `__str__` / `__repr__` on configuration classes (e.g., `AudioFilterConfig`) to improve logging readability.
  - Expand `speech_manager/readme.md` with examples of tuning `AudioFilterConfig` for different mics/environments.
  - Add a top-level CONTRIBUTING.md describing how to run and test locally.

Where to look for examples
--------------------------
- `other/test_stt.py` — small test harness for STT
- `src/utils/test_tts.py` — unit/demo for TTS

Notes
-----
- Vosk models are large; download only the models you need.
- Audio hardware and drivers are environment-dependent — if audio capture fails, test with `sounddevice.query_devices()`.

Contributing
------------
- Fork, add/extend docstrings, tests and raise PRs. Prefer small, focused doc or code changes.

License
-------
- No explicit license file detected; add LICENSE if intended for public distribution.
