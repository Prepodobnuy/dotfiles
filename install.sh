#!/bin/bash

echo "installing dependencies"
paru -S hyprland rust qt5ct-kde qt6ct-kde dolphin elisa waybar swaync swaybg xdg-desktop-portal xdg-desktop-portal-hyprland-git xdg-desktop-portal-gtk xdg-utils neovim alacritty nwg-look hyprshotgun fish rofi-wayland

echo "installing fonts"
paru -S otf-font-awesome ttf-jetbrains-mono-nerd

echo "installing rpaper"
git clone https://github.com/Prepodobnuy/rpaper.git
cd rpaper
cargo install --path .
sudo rm /usr/bin/rpaper
sudo mv ~/.cargo/bin/rpaper /usr/bin/rpaper
cd ..
rm -rf rpaper
mkdir -p ~/.cache/rpaper/
mkdir -p ~/.cache/rpaper/rwal/
mkdir -p ~/.cache/rpaper/Wallpapers/
mkdir -p ~/Documents/
mkdir -p ~/Documents/Wallpapers/

echo "changing .config"
cp -rf .config/ ~/.config/

echo "changing .themes"
cp -rf .themes/ ~/.themes/

echo "change display size params in ~/.config/hypr/hyprland.conf and ~/.config/rpaper/config.json"
echo "dont forget to put some wallpapers in ~/Documents/Wallpapers/ to rpaper properly work"
echo "bye"
