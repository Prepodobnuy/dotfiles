#!/bin/bash

paru -S python imv python-pip otf-font-awesome swww feh pywal alacritty nemo rofi-lbonn-wayland-git waybar hyprshotgun ttf-jetbrains-mono-nerd ttf-terminus-nerd
pip install colorz pillow --break-system-packages

mkdir ~/.my_script_files
mkdir ~/.config/alacritty
mkdir ~/.config/hypr
mkdir ~/.config/rofi
mkdir ~/.config/waybar
mkdir ~/Documents
mkdir ~/Documents/Wallpapers
mkdir ~/Documents/CachedWallpapers

cp -r .config/alacritty ~/.config/alacritty
cp -r .config/hypr ~/.config/hypr
cp -r .config/rofi ~/.config/rofi
cp -r .config/waybar ~/.config/waybar
cp -r .my_script_files ~/.my_script_files