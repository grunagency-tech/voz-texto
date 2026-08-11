#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
import time

PID_FILE = "/tmp/superwhisper.pid"
WAV_FILE = "/tmp/superwhisper.wav"

def notify(title, msg, timeout=1200):
    subprocess.run(["notify-send", "-t", str(timeout), "-h", "string:x-canonical-private-synchronous:superwhisper", title, msg])

def auto_paste(text):
    # 1. Copiar al portapapeles de Wayland y X11
    p = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE, text=True)
    p.communicate(input=text)

    try:
        p2 = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, text=True)
        p2.communicate(input=text)
    except Exception:
        pass

    # 2. Esperar a que se libere la tecla Super
    time.sleep(0.35)

    # 3. Pegar usando ydotool
    subprocess.run(["ydotool", "key", "--delay", "50", "ctrl+v"], stderr=subprocess.DEVNULL)
    subprocess.run(["ydotool", "key", "--delay", "50", "ctrl+shift+v"], stderr=subprocess.DEVNULL)

def start_recording():
    if os.path.exists(WAV_FILE):
        try:
            os.remove(WAV_FILE)
        except Exception:
            pass

    proc = subprocess.Popen(["pw-record", WAV_FILE])
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    
    notify("🎙️ Grabando...", "Habla ahora... Presiona Windows+Q al terminar", 2000)

def stop_recording():
    if not os.path.exists(PID_FILE):
        notify("⚠️ Info", "No hay grabación activa", 1200)
        return

    with open(PID_FILE, "r") as f:
        pid_str = f.read().strip()

    try:
        pid = int(pid_str)
        os.kill(pid, signal.SIGINT)
    except Exception:
        pass

    try:
        os.remove(PID_FILE)
    except Exception:
        pass

    notify("⚡ Transcribiendo...", "Procesando audio...", 1200)
    
    # Esperar a que pw-record termine de volcar el archivo al disco (máx 0.5s)
    for _ in range(10):
        if os.path.exists(WAV_FILE) and os.path.getsize(WAV_FILE) > 44:
            break
        time.sleep(0.05)

    if not os.path.exists(WAV_FILE) or os.path.getsize(WAV_FILE) <= 44:
        notify("⚠️ Info", "Grabación muy corta (menos de 0.1s)", 1200)
        return

    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("small", device="cpu", compute_type="int8")
        segments, info = model.transcribe(WAV_FILE, beam_size=5)
        text = " ".join([seg.text.strip() for seg in segments]).strip()

        if not text:
            notify("⚠️ Silencio", "No se detectó voz", 1200)
            return

        # Auto-pegado directo
        auto_paste(text)
        notify("✅ Copiado al portapapeles", f'"{text[:45]}..."', 1500)

    except Exception as e:
        notify("❌ Error", str(e), 2000)

if __name__ == "__main__":
    if os.path.exists(PID_FILE):
        stop_recording()
    else:
        start_recording()
