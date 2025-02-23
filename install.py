#!/usr/bin/python3
import os
import shutil

PACKAGES = [
    "--needed",
    "hyprland",
    "aquamarine",
    "hyprcursor",
    "hyprgraphics",
    "hyprshotgun",
    "xdg-desktop-portal",
    "xdg-desktop-portla-hyprland",
    "qt5ct-kde qt6ct-kde dolphin elisa",
    "nwg-look waybar swaync swaybg",
    "rofi-wayland",
    "fish",
    "swaybg",
    "rust",
    "helix",
    "alacritty",
    "firefox",
    "make",
    "imagemagick",
    "bash grep sed bc glib2 gdk-pixbuf2 sassc gtk-engine-murrine gtk-engines librsvg",
]

ADDITIONAL_PACKAGES = [
    "vesktop-bin",
    "thunderbird",
    "onlyoffice-bin",
    "opentabletdriver",
]

FONTS = [
    "otf-font-awesome",
    "ttf-jetbrains-mono-nerd",
]

def ask(prompt: str, some_variable_name_here_lol: dict): 
    keys = some_variable_name_here_lol.keys()
    responce = ''
    while not responce in keys:
        responce = input(f"{prompt} [{", ".join([key for key in keys])}]: ")
    return some_variable_name_here_lol[responce]

def install(packages: list[str]):
    os.system(f"paru -Sy {" ".join(packages)}")

def main():
    install_fonts = ask("Do you want to install fonts?", {"y":True, "n":False})
    install_a_packages = ask("Do you want to install additional packages?", {"y":True, "n":False})

    print("Installing necessary packages..")
    install(PACKAGES)
    if install_fonts: print("Installing fonts.."); install(FONTS)
    if install_a_packages: print("Installing aditional packages..");  install(ADDITIONAL_PACKAGES)

    current_directory = os.path.abspath(".")

    print("Installing rpaper..")
    os.system(f"git clone https://github.com/Prepodobnuy/rpaper; mv rpaper /tmp/rpaper")
    os.chdir(f"/tmp/rpaper/")
    os.system("make install")
    os.chdir(current_directory)
    shutil.rmtree("/tmp/rpaper")

    print("Moving dotfiles..")
    for config in os.listdir(".config"):
        try:
            os.rename(f"/.config/{config}", os.path.expanduser(f"~/.config/{config}"))
            print(f"/.config/{config}", "->", os.path.expanduser(f"~/.config/{config}"))
        except Exception:...

    print("YAY")


if __name__ == "__main__":
    main()