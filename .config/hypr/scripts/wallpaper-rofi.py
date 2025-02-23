#!/usr/bin/env python3
#
# This script allows to set wallpapers and color schemes using rofi.
# created by https://github.com/Prepodobnuy <prepodobnuy@inbox.ru>
#
# dependencies:
#   imagemagick
#   rofi
#   rpaper https://github.com/Prepodobnuy/rpaper
#
# if you are going to use the built-in theme (rofi-wide.template), 
# then ttf-jetbrains-mono will also be a dependency

import sys
import os
import subprocess


HELP_MESSAGE = "usage: \n  python rpaper-rofi.py <path/to/dir/with/pictures>"
THUMB_DIR = os.path.expanduser('~/.cache/rpaper/thumbs')

def thumb_image(file_path, file_name):
    """
    Function to thumb->save images.
    Needed to display wallpapers in rofi.
    """
    if not os.path.exists(f"{THUMB_DIR}/{file_name}.thmb"):
        os.system(f'magick "{file_path}" -strip -thumbnail 500x500^ -gravity center -extent 500x500 "{THUMB_DIR}/{file_name}.thmb"')
    return f'{THUMB_DIR}/{file_name}.thmb'


class Wallpaper(object):
    """
    hack class :p
    """
    def __init__(self, path: str, tags: list) -> None:
        self.path = path
        self.last_path_entity = self.path.split('/')[-1] if '/' in self.path else self.path
        self.tags = f'[{", ".join(tags)}]' if tags else None
        self.name = self.__process_name()
        self.thumb_path = thumb_image(self.path, self.last_path_entity)

    def __process_name(self) -> str:
        name = self.last_path_entity.split('.')[0] if '.' in self.last_path_entity else self.last_path_entity
        if self.tags: name += ' ' + self.tags
        return name

    def __lt__(self, other) -> bool:
        if isinstance(other, Wallpaper):
            return self.__repr__() < other.__repr__()
        return NotImplemented


def list_wallpapers(dir: str, tags: list = []) -> list[Wallpaper]:
    """
    Recursive function to collect 
    images from the original directory.

    Each directory besides the main one 
    will be added to the image as a tag.
    """
    res: list[str] = []
    entries: list[str] = os.listdir(dir)

    for entry in entries:
        path = f'{dir}/{entry}'
        if os.path.isfile(path):
            res.append(Wallpaper(path, tags))
            continue
        if os.path.isdir(path):
            res += list_wallpapers(path, tags + [path.split('/')[-1]])
    
    return res


if __name__ == "__main__":
    if not os.path.exists(THUMB_DIR):
        try:
            os.makedirs(os.path.expanduser("~/.cache/rpaper"), exist_ok=True)
        except Exception as e:...
        try:
            os.makedirs(THUMB_DIR, exist_ok=True)
        except Exception as e:...
    
    # receiving the wallpapers path 
    if len(sys.argv) < 2 or '--help' in sys.argv:
        print(HELP_MESSAGE)
        sys.exit(1)

    path = os.path.expanduser(sys.argv.pop())
    if path.endswith('/'):
        path = path[:-1]

    # collecting image files
    wallpapers = sorted(list_wallpapers(path))
    names = [wallpaper.name for wallpaper in wallpapers]
    icons = '\0\n'.join(f'{wallpaper.name}\0icon\x1f{wallpaper.thumb_path}' for wallpaper in wallpapers)

    # setting rofi variables
    config_path = '~/.config/rofi/config-wide.rasi'

    # running rofi
    rofi = subprocess.run(
        ['rofi', '-dmenu', '-config' , config_path],
        input=icons,
        text=True,
        capture_output=True,
    )

    # running rpaper
    if rofi.stdout:
        path = wallpapers[names.index(rofi.stdout.strip())].path
        command = f'killall swaybg; rpaper -S -T -I "{path}"'
        os.system(command)
        with open(os.path.expanduser("~/.rpaper.sh"), 'w') as file:
            file.write(command)
