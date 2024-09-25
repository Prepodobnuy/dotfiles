import sys
import os
import subprocess
import datetime


class Wallpaper(object):
    def __init__(self, path: str, tag: str) -> None:
        self.path = path
        self.tag = tag

    def __repr__(self) -> str:
        if self.tag:
            return f"[{self.tag}] {self.path}"
        return self.path

    def __str__(self) -> str:
        if self.tag:
            return f"[{self.tag}] {self.path}"
        return self.path

    def __lt__(self, other):
        if isinstance(other, Wallpaper):
            return self.__repr__() < other.__repr__()
        return NotImplemented


def get_wallpapers(directory: str, tag: str) -> list[Wallpaper]:
    res: list[Wallpaper] = []
    entries = os.listdir(directory)

    for entry in entries:
        file = f"{directory}/{entry}"
        if os.path.isdir(file):
            res += get_wallpapers(file, tag + ", " + entry if tag != "" else entry)
        elif os.path.isfile(file):
            res.append(Wallpaper(file, tag))

    return res


if __name__ == "__main__":
    path = sys.argv.pop()
    path.replace("~", os.getenv("HOME"), 1)
    path = path[::-1][1:][::-1] if path[-1] == "/" else path

    wallpapers = sorted(get_wallpapers(path, ""))
    wallpaper_tags_names = [
        f"{('[' + wallpaper.tag + ']') if wallpaper.tag else ''} {wallpaper.path.split('/')[-1]}"
        for wallpaper in wallpapers
    ]
    wallpaper_paths = [wallpaper.path for wallpaper in wallpapers]
    rofi = subprocess.run(
        ["rofi", "-dmenu", "-config", "~/.config/rofi/config-wide.rasi"],
        input="\n".join(wallpaper_tags_names),
        text=True,
        capture_output=True,
    )

    light_theme_hour_limits = (10, 18)
    hour = int(datetime.datetime.now().strftime("%H"))

    if hour >= light_theme_hour_limits[0] and hour <= light_theme_hour_limits[1]:
        message = "--colors ~/.config/rpaper/color_variables_light.json"
    else:
        message = ""

    if rofi.stdout:
        os.system(
            f"rpaper {wallpaper_paths[wallpaper_tags_names.index(rofi.stdout[::-1][1:][::-1])]} {message}"
        )
