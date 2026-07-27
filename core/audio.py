
import subprocess
import os
import tempfile
import threading
import shutil
import logging

logger = logging.getLogger(__name__)

_PLAYERS = ["mpv", "ffplay", "aplay", "paplay"]

def _find_player():
    for p in _PLAYERS:
        if shutil.which(p):
            return p
    return None

def _is_installed(cmd):
    if shutil.which(cmd):
        return True
    common = ["/usr/bin/" + cmd, "/usr/local/bin/" + cmd,
              "/opt/homebrew/bin/" + cmd, "C:\\Program Files\\" + cmd]
    return any(os.path.exists(p) for p in common)

def speak(text, lang="en"):
    if not text:
        return
    t = threading.Thread(target=_speak_sync, args=(text, lang), daemon=True)
    t.start()

def speak_sequence(segments):
    if not segments:
        return
    t = threading.Thread(target=_speak_sequence_sync, args=(segments,), daemon=True)
    t.start()

def _speak_sequence_sync(segments):
    for text, lang in segments:
        _speak_sync(text, lang)

def _speak_sync(text, lang):
    try:
        if _is_installed("edge-tts"):
            voice = {"en": "en-US-JennyNeural", "vi": "vi-VN-HoaiMyNeural",
                     "zh": "zh-CN-XiaoxiaoNeural"}.get(lang, "en-US-JennyNeural")
            tmp = tempfile.mktemp(suffix=".mp3")
            try:
                r = subprocess.run(["edge-tts", "--voice", voice, "--text", text,
                                    "--write-media", tmp],
                                  capture_output=True, timeout=20)
                if r.returncode == 0 and os.path.isfile(tmp) and os.path.getsize(tmp) > 0:
                    player = _find_player()
                    if player:
                        subprocess.run([player, tmp],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        logger.warning("edge-tts tạo file OK nhưng không có trình phát nào (mpv/ffplay/aplay/paplay)")
                    _try_remove(tmp)
                    return
                logger.warning("edge-tts thất bại: returncode=%s, stderr=%s",
                               r.returncode, r.stderr.decode(errors="replace")[:200])
            except Exception as e:
                logger.warning("edge-tts lỗi: %s", e)
                _try_remove(tmp)

        if _is_installed("gtts-cli"):
            glang = {"en": "en", "vi": "vi", "zh": "zh-CN"}.get(lang, "en")
            tmp = tempfile.mktemp(suffix=".mp3")
            try:
                r = subprocess.run(["gtts-cli", "--lang", glang, text, "--output", tmp],
                                  capture_output=True, timeout=20)
                if r.returncode == 0 and os.path.isfile(tmp) and os.path.getsize(tmp) > 0:
                    player = _find_player()
                    if player:
                        subprocess.run([player, tmp],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        logger.warning("gtts-cli tạo file OK nhưng không có trình phát nào")
                    _try_remove(tmp)
                    return
                logger.warning("gtts-cli thất bại: returncode=%s", r.returncode)
            except Exception as e:
                logger.warning("gtts-cli lỗi: %s", e)
                _try_remove(tmp)

        if _is_installed("espeak-ng"):
            v = {"en": "en-us", "vi": "vi", "zh": "zh"}.get(lang, "en-us")
            subprocess.run(["espeak-ng", "-v", v, text],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return

        if _is_installed("espeak"):
            subprocess.run(["espeak", text],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return

        logger.warning("Không tìm thấy công cụ TTS nào (edge-tts/gtts-cli/espeak-ng/espeak) cho: %r", text[:50])
    except Exception as e:
        logger.error("Lỗi không xác định khi phát âm '%s': %s", text[:50], e)

def _try_remove(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
    except Exception as e:
        logger.debug("Không xoá được file tạm %s: %s", path, e)
