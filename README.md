# 🎙️ Groon Voice-to-Text (Superwhisper para Linux / Wayland)

Herramienta de dictado rápido por voz **100% local, privada y sin lag**, optimizada para Linux (Zorin OS, Ubuntu, Fedora / Silverblue) en entornos Wayland / GNOME.

Ideal para dictar prompts a **AGY, Claude Code, OpenCode, VS Code, Slack o navegador**.

---

## ⚡ Instalación rápida (1 paso)

Clona este repositorio y corre el instalador:

```bash
git clone https://github.com/grunagency-tech/groon-voz-a-texto.git
cd groon-voz-a-texto
./install.sh
```

---

## 🚀 Cómo se usa

1. Pon el cursor en cualquier campo de texto.
2. Presiona **`Windows + Q`** ➜ Verás la notificación `🎙️ Grabando...`.
3. Habla tu prompt o texto.
4. Presiona **`Windows + Q`** al terminar ➜ El texto se transcribirá en **menos de 1 segundo** y **se pegará automáticamente** en tu pantalla.

---

## 🛠️ Características

- 🎙️ **PipeWire Native**: Captura audio de alta fidelidad directamente desde tu micrófono (ej. Blue Yeti).
- 🧠 **faster-whisper (int8)**: Transcripción local super rápida sin enviar nada a servidores externos.
- ⌨️ **Auto-paste en Wayland**: Usa `ydotool` para pegar automáticamente sin depender de herramientas X11 antiguas.
- 🔒 **100% Offline**: Funciona sin internet y sin suscripciones.
