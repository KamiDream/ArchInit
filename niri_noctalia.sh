#!/bin/bash

# Arch Linux initialization script — fully automated one-click setup
# Run this script as a normal user with sudo privileges.
# All steps run sequentially after initial privilege escalation.
#
# This variant replaces DMS (Display Manager Switcher) with Noctalia,
# a modern Wayland desktop shell providing bars, widgets, launcher,
# notifications, lock screen, wallpapers, and more — all integrated
# as one cohesive shell around your compositor.
#
# Noctalia v5 is built directly on Wayland and OpenGL ES (no Qt/GTK).
# Website: https://noctalia.dev
# Docs:    https://docs.noctalia.dev/v5/

set -Euo pipefail

# ─── Error handling ──────────────────────────
# Display a clear error message on failure, then exit
error_handler() {
    local exit_code=$?
    echo "" >&2
    echo -e "${RED}${BOLD}  ❌ Error at line $1 — exit code $exit_code${RESET}" >&2
    echo -e "${RED}  Please fix the issue and re-run the script.${RESET}" >&2
    echo "" >&2
    exit "$exit_code"
}
trap 'error_handler $LINENO' ERR

# Ensure cleanup on Ctrl+C
cleanup() {
    echo "" >&2
    echo -e "${YELLOW}  ⚠️  Script interrupted by user.${RESET}" >&2
    exit 1
}
trap 'cleanup' INT
# ─────────────────────────────────────────────

# ─── Color definitions ───────────────────────
GREEN='\e[32m'
RED='\e[31m'
YELLOW='\e[33m'
CYAN='\e[36m'
LIGHT_BLUE='\e[94m'
LIGHT_PINK='\e[95m'
RESET='\e[0m'
BOLD='\e[1m'
# ─────────────────────────────────────────────

print_logo() {
    while IFS= read -r line; do
        echo -e "${LIGHT_BLUE}${line:0:48}${LIGHT_PINK}${line:48}${RESET}"
    done << 'LOGO'
88      a8P                                   88  88888888ba,
88    ,88'                                    ""  88      `"8b
88  ,88"                                          88        `8b
88,d88'       ,adPPYYba,  88,dPYba,,adPYba,   88  88         88  8b,dPPYba,   ,adPPYba,  ,adPPYYba,  88,dPYba,,adPYba,
8888"88,      ""     `Y8  88P'   "88"    "8a  88  88         88  88P'   "Y8  a8P_____88  ""     `Y8  88P'   "88"    "8a
88P   Y8b     ,adPPPPP88  88      88      88  88  88         8P  88          8PP"""""""  ,adPPPPP88  88      88      88
88     "88,   88,    ,88  88      88      88  88  88      .a8P   88          "8b,   ,aa  88,    ,88  88      88      88
88       Y8b  `"8bbdP"Y8  88      88      88  88  88888888Y"'    88           `"Ybbd8"'  `"8bbdP"Y8  88      88      88
LOGO
}

# ─────────────────────────────────────────────
# Initial privilege escalation & keep-alive
# ─────────────────────────────────────────────
print_logo
echo "═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════"
echo "  ArchInit — One-Click Setup (Noctalia Edition)"
echo "═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════"
echo ""
echo ">>> Requesting sudo access (password required)..."
sudo -v

# Keep sudo session alive in the background
while true; do sudo -n true; sleep 60; kill -0 "$$" 2>/dev/null || break; done 2>/dev/null &

echo "    ✅ Sudo privileges acquired."
echo ""

# ─────────────────────────────────────────────
# Step 1: Core Desktop (Niri)
# ─────────────────────────────────────────────
echo "========================================================================================================================="
echo " Step 1: Core Desktop (Niri)"
echo "========================================================================================================================="
echo ">>> Installing Niri and related components..."
sudo pacman -Syu --needed --noconfirm niri xwayland-satellite xdg-desktop-portal-gnome \
    xdg-desktop-portal-gtk kitty matugen cava \
    qt6-multimedia-ffmpeg power-profiles-daemon kimageformats greetd

echo "[Step 1 completed]"
echo ""

# ─────────────────────────────────────────────
# Step 2: Install AUR Helper & Noctalia Shell
# ─────────────────────────────────────────────
echo "========================================================================================================================="
echo " Step 2: Install AUR Helper & Noctalia Shell"
echo "========================================================================================================================="

# 2a. Configure archlinuxcn repository and install AUR helpers
echo ">>> Configuring /etc/pacman.conf..."
# Uncomment [multilib] and its Include line
sudo sed -i '/^#\[multilib\]/,/^#Include/ s/^#//' /etc/pacman.conf
echo "    [multilib] enabled."
# Add archlinuxcn repository if not already present
if ! grep -q '^\[archlinuxcn\]' /etc/pacman.conf; then
    sudo tee -a /etc/pacman.conf > /dev/null << 'EOF'

[archlinuxcn]
Server = https://mirrors.ustc.edu.cn/archlinuxcn/$arch
Server = https://mirrors.tuna.tsinghua.edu.cn/archlinuxcn/$arch
Server = https://mirrors.hit.edu.cn/archlinuxcn/$arch
Server = https://repo.huaweicloud.com/archlinuxcn/$arch
EOF
    echo "    [archlinuxcn] repository added."
else
    echo "    [archlinuxcn] already present, skipping."
fi
echo ">>> Installing archlinuxcn-keyring and AUR helpers..."
sudo pacman -Sy --needed --noconfirm archlinuxcn-keyring
sudo pacman -S --needed --noconfirm base-devel yay paru
sudo pacman -Syu --noconfirm
echo "    ✅ AUR helpers (yay, paru) installed."

# 2b. Install Noctalia from AUR (v5, built on Wayland + OpenGL ES)
echo ""
echo ">>> Installing Noctalia shell from AUR (noctalia-git)..."
yay -S --needed --noconfirm noctalia-git
echo "    ✅ Noctalia installed."

# 2c. Configure Niri to autostart Noctalia and add window rules / keybinds
echo ""
echo ">>> Configuring Niri to autostart Noctalia..."
NIRI_CONFIG="$HOME/.config/niri/config.kdl"
mkdir -p "$(dirname "$NIRI_CONFIG")"

if [[ ! -f "$NIRI_CONFIG" ]]; then
    # Create minimal Niri config
    cat > "$NIRI_CONFIG" << 'NIRIEOF'
# Niri configuration — automatically generated by ArchInit (Noctalia Edition)
# See https://github.com/YaLTeR/niri/wiki/Configuration for details

# ─── Noctalia desktop shell ──────────────────────────────────────────────
spawn-at-startup "noctalia"

# ─── Window appearance ───────────────────────────────────────────────────
window-rule {
    geometry-corner-radius 20
    clip-to-geometry true
}

# Floating Noctalia settings window
window-rule {
    match app-id="dev.noctalia.Noctalia"
    open-floating true
    default-column-width { fixed 1080; }
    default-window-height { fixed 920; }
}

debug {
    # Allows notification actions and window activation from Noctalia
    honor-xdg-activation-with-invalid-serial
}

# ─── Keybinds ────────────────────────────────────────────────────────────
binds {
    # Core Noctalia binds
    Mod+Space          { spawn-sh "noctalia msg panel-toggle launcher"; }
    Mod+S              { spawn-sh "noctalia msg panel-toggle control-center"; }
    Mod+Comma          { spawn-sh "noctalia msg settings-toggle"; }

    # Audio & Brightness
    XF86AudioRaiseVolume   { spawn-sh "noctalia msg volume-up"; }
    XF86AudioLowerVolume   { spawn-sh "noctalia msg volume-down"; }
    XF86AudioMute          { spawn-sh "noctalia msg volume-mute"; }
    XF86MonBrightnessUp    { spawn-sh "noctalia msg brightness-up"; }
    XF86MonBrightnessDown  { spawn-sh "noctalia msg brightness-down"; }
}
NIRIEOF
    echo "    ✅ Minimal Niri config created at ~/.config/niri/config.kdl"
else
    # Check if noctalia autostart is already configured
    if grep -q 'spawn-at-startup.*noctalia' "$NIRI_CONFIG" 2>/dev/null; then
        echo "    Noctalia autostart already present in Niri config, skipping."
    else
        echo ""
        echo "    ⚠️  Existing Niri config found at ~/.config/niri/config.kdl"
        echo "    Please manually add the following line to autostart Noctalia:"
        echo ""
        echo '      spawn-at-startup "noctalia"'
        echo ""
        echo "    See https://docs.noctalia.dev/v5/compositor-settings/niri/ for"
        echo "    recommended window rules and keybinds."
    fi
fi

# 2d. Create default Noctalia configuration
echo ""
echo ">>> Creating default Noctalia configuration..."
NOCTALIA_CONFIG="$HOME/.config/noctalia/config.toml"
mkdir -p "$(dirname "$NOCTALIA_CONFIG")"

if [[ ! -f "$NOCTALIA_CONFIG" ]]; then
    cat > "$NOCTALIA_CONFIG" << 'NOCTOML'
# Noctalia configuration — auto-generated by ArchInit (Noctalia Edition)
# See https://docs.noctalia.dev/v5/configuration/ for full reference.

[shell]
font_family           = "sans-serif"
corner_radius_scale   = 1.0
time_format           = "{:%H:%M}"
date_format           = "%A, %x"
clipboard_enabled     = true
polkit_agent          = false

[shell.panel]
transparency_mode     = "solid"
borders               = true
shadow                = true

[shell.animation]
enabled = true
speed   = 1.0

[wallpaper]
enabled   = true
fill_mode = "crop"
directory = "~/Pictures/Wallpapers"

[wallpaper.automation]
enabled          = false
interval_minutes = 0
order            = "random"

[theme]
mode    = "dark"
source  = "builtin"
builtin = "Noctalia"
NOCTOML
    echo "    ✅ Default Noctalia config created at ~/.config/noctalia/config.toml"
else
    echo "    Noctalia config already exists, skipping."
fi

echo "[Step 2 completed]"
echo ""

# ─────────────────────────────────────────────
# Step 3: Basic Initialization
# ─────────────────────────────────────────────
echo "========================================================================================================================="
echo " Step 3: Basic Initialization"
echo "========================================================================================================================="
echo ">>> Installing base packages..."
sudo pacman -S --needed --noconfirm fastfetch fcitx5-im fcitx5-rime fuse2 ntfs-3g git \
    quickshell flatseal dolphin kate firefox

echo ""
echo ">>> Uncommenting zh_CN.UTF-8 in /etc/locale.gen..."
sudo sed -i 's/^#zh_CN.UTF-8/zh_CN.UTF-8/' /etc/locale.gen
echo "    zh_CN.UTF-8 enabled."

echo ">>> Generating locale..."
sudo locale-gen
echo ">>> Setting system locale to zh_CN.UTF-8..."
sudo localectl set-locale LANG=zh_CN.UTF-8

echo ">>> Installing Chinese fonts & Nerd fonts..."
sudo pacman -S --needed --noconfirm wqy-microhei wqy-microhei-lite wqy-bitmapfont wqy-zenhei \
    ttf-arphic-ukai ttf-arphic-uming noto-fonts-cjk ttf-jetbrains-mono-nerd noto-fonts-emoji

echo "[Step 3 completed]"
echo ""

# ─────────────────────────────────────────────
# Step 4: Display Manager (Noctalia Greeter)
# ─────────────────────────────────────────────
echo "========================================================================================================================="
echo " Step 4: Display Manager (Noctalia Greeter)"
echo "========================================================================================================================="

echo ">>> Installing Noctalia Greeter from AUR..."
yay -S --needed --noconfirm noctalia-greeter
echo "    ✅ Noctalia Greeter installed."

echo ""
echo ">>> Configuring greetd to use Noctalia Greeter..."
GREETD_CONFIG="/etc/greetd/config.toml"
GREETER_SESSION_PATH=""

# Find the noctalia-greeter-session binary
if command -v noctalia-greeter-session &>/dev/null; then
    GREETER_SESSION_PATH="$(command -v noctalia-greeter-session)"
elif [[ -x /usr/local/bin/noctalia-greeter-session ]]; then
    GREETER_SESSION_PATH="/usr/local/bin/noctalia-greeter-session"
elif [[ -x /usr/bin/noctalia-greeter-session ]]; then
    GREETER_SESSION_PATH="/usr/bin/noctalia-greeter-session"
fi

if [[ -z "$GREETER_SESSION_PATH" ]]; then
    echo "    ⚠️  Could not find noctalia-greeter-session binary."
    echo "    Please check the installation and configure /etc/greetd/config.toml manually."
else
    echo "    Found greeter session at: $GREETER_SESSION_PATH"
    # Create greetd config directory
    sudo mkdir -p /etc/greetd

    # Back up existing config if present
    if [[ -f "$GREETD_CONFIG" ]]; then
        sudo cp "$GREETD_CONFIG" "${GREETD_CONFIG}.bak"
        echo "    Existing config backed up to ${GREETD_CONFIG}.bak"
    fi

    # Write greetd config with Noctalia session as default
    sudo tee "$GREETD_CONFIG" > /dev/null << GREETDEOF
[terminal]
vt = 1

[default_session]
command = "${GREETER_SESSION_PATH} -- --session niri"
user = "greeter"
GREETDEOF
    echo "    ✅ greetd config written to $GREETD_CONFIG"
    echo "    Default session set to: niri"
fi

echo ""
echo ">>> Enabling greetd display manager..."
sudo systemctl enable greetd
echo ">>> Starting greetd..."
sudo systemctl start greetd

echo "[Step 4 completed]"
echo ""

# ─────────────────────────────────────────────
# Done
# ─────────────────────────────────────────────
echo "═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════"
echo "  ✅ All steps completed!"
echo ""
echo "  Please re-login or reboot for changes to take effect."
echo ""
echo "  ── What was installed ──"
echo "  • Niri compositor + xwayland-satellite"
echo "  • Noctalia desktop shell (v5) — bars, widgets, launcher, notifications, etc."
echo "  • Noctalia Greeter — login screen (via greetd, replacing LightDM)"
echo "  • Kitty terminal, Matugen, cava, fastfetch, Fcitx5, fonts, and more"
echo ""
echo "  ── Post-install tips ──"
echo "  • Edit ~/.config/noctalia/config.toml to customize the shell (hot-reloaded)"
echo "  • Edit ~/.config/niri/config.kdl to adjust window rules and keybinds"
echo "  • Run 'niri' to start the compositor (or reboot)"
echo "  • Noctalia keybinds: Mod+Space = launcher, Mod+S = control center"
echo "  • Documentation: https://docs.noctalia.dev/v5/"
echo "═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════"
