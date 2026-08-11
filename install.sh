#!/bin/bash
set -e

echo "🚀 Instalando Groon Voice-to-Text..."

# 1. Instalar dependencias según la distribución
if [ -f /etc/fedora-release ]; then
    echo "📦 Detectado Fedora / Silverblue..."
    pip install --user faster-whisper 2>/dev/null || pip3 install faster-whisper --break-system-packages
    which ydotool >/dev/null 2>&1 || sudo rpm-ostree install ydotool || sudo dnf install -y ydotool
else
    echo "📦 Detectado Ubuntu / Zorin OS..."
    sudo apt update
    sudo apt install -y python3-pip ydotool wl-clipboard xclip sox ffmpeg
    pip3 install --break-system-packages faster-whisper 2>/dev/null || pip install faster-whisper
fi

# 2. Permisos uinput para ydotool sin sudo
echo "🔑 Configurando permisos uinput..."
echo 'KERNEL=="uinput", MODE="0666"' | sudo tee /etc/udev/rules.d/99-uinput.rules >/dev/null
sudo udevadm control --reload-rules 2>/dev/null || true
sudo udevadm trigger 2>/dev/null || true
sudo chmod 666 /dev/uinput 2>/dev/null || true

# 3. Copiar script ejecutable
mkdir -p ~/.local/bin ~/bin
cp superwhisper.py ~/.local/bin/superwhisper.py
cp superwhisper.py ~/bin/superwhisper.py
chmod +x ~/.local/bin/superwhisper.py ~/bin/superwhisper.py

# 4. Pre-descargar modelo Whisper
echo "🧠 Pre-descargando modelo Whisper small..."
python3 -c "from faster_whisper import WhisperModel; model = WhisperModel('small', device='cpu', compute_type='int8')"

# 5. Configurar hotkey GNOME (Super+Q)
BASE="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$BASE/custom0/ name "Groon Voice-to-Text"
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$BASE/custom0/ command "$HOME/bin/superwhisper.py"
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$BASE/custom0/ binding "<Super>q"
gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['$BASE/custom0/']"

echo "✅ Instalación completada!"
echo "🎙️ Presiona Windows+Q en cualquier campo de texto para dictar."
