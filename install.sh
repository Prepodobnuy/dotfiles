#!/bin/bash

paru -S python imv qt6ct-kde python-pip otf-font-awesome swaync swww feh pywal alacritty nemo rofi-lbonn-wayland-git waybar hyprshotgun ttf-jetbrains-mono-nerd ttf-terminus-nerd
pip install colorz pillow --break-system-packages

mkdir ~/.my_script_files
mkdir ~/.config/alacritty
mkdir ~/.config/hypr
mkdir ~/.config/qt6ct
mkdir ~/.config/rofi
mkdir ~/.config/rpaper
mkdir ~/.config/swaync
mkdir ~/.config/waybar

cp -r .config/alacritty ~/.config/alacritty
cp -r .config/hypr ~/.config/hypr
cp -r .config/qt6ct ~/.config/qt6ct
cp -r .config/rofi ~/.config/rofi
cp -r .config/rpaper ~/.config/rpaper
cp -r .config/swaync ~/.config/swaync
cp -r .config/waybar ~/.config/waybar
cp -r .my_script_files ~/.my_script_files