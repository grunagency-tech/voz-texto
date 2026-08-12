#!/usr/bin/env python3
"""Local voice dictation for GNOME/Wayland using the Blue Yeti."""

import os
import signal
import subprocess
import time

import numpy as np
import soundfile as sf

PID_FILE = "/tmp/superwhisper.pid"
WAV_FILE = "/tmp/superwhisper.wav"


def notify(title, message, timeout=1600):
    subprocess.run(
        ["notify-send", "-t", str(timeout),
         "-h", "string:x-canonical-private-synchronous:superwhisper",
         title, message],
        check=False,
    )


def yeti_source():
    """Return PipeWire's current Blue Yeti source name, if present."""
    result = subprocess.run(
        ["pactl", "list", "short", "sources"], capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        fields = line.split()
        if (len(fields) > 1 and fields[1].startswith("alsa_input.")
                and "blue_microphones" in fields[1].lower()):
            return fields[1]
    return None


def auto_paste(text):
    subprocess.run(["wl-copy"], input=text, text=True, check=False)
    # Wait until GNOME has received the Super+Q key release, then paste using
    # the terminal/Wayland-safe chord. `ydotool` already proved keyboard
    # injection works here; only the old numeric chord was malformed.
    time.sleep(0.8)
    result = subprocess.run(
        ["ydotool", "key", "--delay", "100", "ctrl+shift+v"],
        capture_output=True, text=True, check=False,
    )
    with open("/tmp/superwhisper-paste.log", "w") as log:
        log.write(f"returncode={result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}\n")


def start_recording():
    source = yeti_source()
    if not source:
        notify("⚠️ Blue Yeti no disponible", "Reconéctalo y confirma que aparece en Sonido.")
        return

    subprocess.run(["pactl", "set-default-source", source], check=False)
    try:
        os.remove(WAV_FILE)
    except FileNotFoundError:
        pass

    # Capture from the Yeti node itself, never from PipeWire's arbitrary default.
    process = subprocess.Popen([
        "pw-record", "--target", source, "--rate", "48000", "--channels", "1",
        "--format", "s16", WAV_FILE,
    ], start_new_session=True)
    with open(PID_FILE, "w") as pid_file:
        pid_file.write(str(process.pid))
    notify("🎙️ Grabando…", "Habla ahora. Presiona Windows+Q al terminar.", 2200)


def normalize_recording():
    audio, rate = sf.read(WAV_FILE, always_2d=False)
    if audio.size == 0:
        return False
    peak = float(np.max(np.abs(audio)))
    # The Yeti can expose a very quiet source after a USB reconnect. Boosting
    # this local temporary recording avoids Whisper mistaking speech for silence.
    if peak < 0.0001:
        return False
    if peak < 0.35:
        audio = np.clip(audio * min(25.0, 0.8 / peak), -1.0, 1.0)
        sf.write(WAV_FILE, audio, rate)
    return True


def stop_recording():
    try:
        with open(PID_FILE) as pid_file:
            pid = int(pid_file.read().strip())
    except (FileNotFoundError, ValueError):
        notify("⚠️ Info", "No hay grabación activa.")
        return

    try:
        os.kill(pid, signal.SIGINT)
    except ProcessLookupError:
        pass
    for _ in range(30):
        try:
            os.kill(pid, 0)
            time.sleep(0.1)
        except ProcessLookupError:
            break
    try:
        os.remove(PID_FILE)
    except FileNotFoundError:
        pass

    if not os.path.exists(WAV_FILE) or os.path.getsize(WAV_FILE) <= 44:
        notify("⚠️ Grabación corta", "No se pudo guardar audio.")
        return
    try:
        if not normalize_recording():
            notify("⚠️ Silencio", "El Yeti no entregó señal de audio.")
            return
        notify("⚡ Transcribiendo…", "Procesando audio localmente…")
        from faster_whisper import WhisperModel
        model = WhisperModel("small", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(WAV_FILE, beam_size=5, language="es")
        text = " ".join(segment.text.strip() for segment in segments).strip()
        if not text:
            notify("⚠️ Silencio", "No se detectó voz.")
            return
        auto_paste(text)
        notify("✅ Dictado listo", f'"{text[:45]}…"', 1800)
    except Exception as exc:
        notify("❌ Error", str(exc), 3000)


if __name__ == "__main__":
    if os.path.exists(PID_FILE):
        stop_recording()
    else:
        start_recording()
