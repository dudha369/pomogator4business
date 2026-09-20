import asyncio

from config import WHISPER_MODEL_SIZE

_model = None
_model_lock = asyncio.Lock()


async def _get_model():
    global _model
    if _model is not None:
        return _model

    async with _model_lock:
        if _model is None:
            from faster_whisper import WhisperModel

            _model = await asyncio.to_thread(
                WhisperModel, WHISPER_MODEL_SIZE, device="cpu", compute_type="int8"
            )
    return _model


async def transcribe_audio(file_path):
    model = await _get_model()

    def _run():
        segments, _info = model.transcribe(file_path)
        return " ".join(segment.text.strip() for segment in segments).strip()

    return await asyncio.to_thread(_run)
