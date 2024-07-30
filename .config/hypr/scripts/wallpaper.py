import os
import sys
import time
import random
import subprocess

import json

from PIL import Image


HOME = os.getenv("HOME")
DEBUG = False


class Config(object):
    def __init__(self) -> None:
        config_path = sys.argv[1]
        with open(config_path) as file:
            self.config_data = json.loads(file.read())

        self.raw_displays_params: dict = self.try_to_set("displays")

        self.colors_variables: list[dict] = self.try_to_set("colors_variables")

        print(self.colors_variables)

        self.wallpapers_dir: str = f"{HOME}".join(
            self.try_to_set("wallpapers_dir").split("$(HOME)")
        )
        self.cached_wallpapers_dir: str = f"{HOME}".join(
            self.try_to_set("cached_wallpapers_dir").split("$(HOME)")
        )
        self.wal_colors_dir: str = f"{HOME}".join(
            self.try_to_set("wal_colors_dir").split("$(HOME)")
        )
        self.template_config_dir: str = f"{HOME}".join(
            self.try_to_set("template_config_dir").split("$(HOME)")
        )
        self.wal_backend: str = self.try_to_set("wal_backend")
        self.wal_bg_color: str = self.try_to_set("wal_bg_color")
        self.swww_params: str = self.try_to_set("swww_params")
        self.sleep_time: int = self.try_to_set("sleep_time")
        self.light_theme: bool = self.try_to_set("light_theme")
        self.resize_displays: bool = self.try_to_set("resize_displays")

    def try_to_set(self, param: str) -> any:
        try:
            return self.config_data[param]
        except Exception as e:
            return None

    def read_args(self) -> None:
        def runrofi(wallpapers) -> list[str]:
            result = subprocess.run(
                ["rofi", "-dmenu", "-p"],
                input="\n".join(wallpapers).encode(),
                stdout=subprocess.PIPE,
            )
            return result.stdout.decode()

        def in_args(params: list[str]) -> bool:
            for param in params:
                if param in sys.argv:
                    return True
            return False

        def get_value_from_args(params: list[str]) -> str | None:
            for param in params:
                if param in sys.argv:
                    return sys.argv[sys.argv.index(param) + 1]
            return None

        runcount = -1
        if in_args(["-wd", "--wallpaper-dir"]):
            self.wallpapers_dir = get_value_from_args(["-wd", "--wallpaper-dir"])
        if in_args(["-cwd", "--cached-wallpaper-dir"]):
            self.cached_wallpapers_dir = get_value_from_args(
                ["-cwd", "--cached-wallpaper-dir"]
            )
        if in_args(["-pcd", "--pywal-colors-dir"]):
            self.wal_colors_dir = get_value_from_args(["-pcd", "--pywal-colors-dir"])
        if in_args(["-c", "--conf"]):
            self.template_config_dir = get_value_from_args(["-c", "--conf"])
        if in_args(["-pb", "--pywal-backend"]):
            self.wal_backend = get_value_from_args(["-pb", "--pywal-backend"])
        if in_args(["-pbc", "--pywal-backgroundcolor"]):
            self.wal_bg_color = get_value_from_args(["-pbc", "--pywal-backgroundcolor"])
        if in_args(["--swww"]):
            self.swww_params = get_value_from_args(["--swww"])
        if in_args(["-s", "--sleep-time"]):
            self.sleep_time = int(get_value_from_args(["-s", "--sleep-time"]))
        if in_args(["-l", "--light"]):
            self.light_theme = True
        if in_args(["--resize-displays"]):
            self.resize_displays = True
        if in_args(["--cache-all"]):
            for wallpaper in os.listdir(self.wallpapers_dir):
                cache_wallpaper(wallpaper_name=wallpaper)
        if in_args(["--once"]):
            runcount = 1
        wallpaperName = random.choice(os.listdir(self.wallpapers_dir))
        if in_args(["-r", "--rofi"]):
            wallpaperName = runrofi(os.listdir(self.wallpapers_dir))
            runcount = 1

        return runcount, wallpaperName


CONFIG = Config()


class Display(object):
    def __init__(
        self, name: str, width: int, height: int, margin_x: int = 0, margin_y: int = 0
    ) -> None:
        self.name: str = name
        self.w: int = width
        self.h: int = height
        self.x: int = margin_x
        self.y: int = margin_y
        self.image: Image = None

    def max_width(displays: list) -> int:
        res = 0
        for display in displays:
            res = display.w + display.x if display.w + display.x > res else res
        return res

    def max_height(displays: list) -> int:
        res = 0
        for display in displays:
            res = display.h + display.y if display.h + display.y > res else res
        return res


class Template(object):
    def __init__(
        self,
        templatepath,
        configfilepath,
        usequotes=False,
        usesharps=False,
        command=None,
        opacity="",
    ) -> None:
        self.templatefilepath = templatepath
        self.configfilepath = configfilepath
        self.executeAfter = command
        self.usequotes = usequotes
        self.usesharps = usesharps
        self.opacity = opacity

    def apply(self, colors: list[str]) -> None:
        variables = CONFIG.colors_variables

        with open(self.templatefilepath, "r") as template:
            data = template.read()

        for variable in variables:
            data = data.split(variable["name"])
            color = colors[variable["value"]]
            tmp = color + self.opacity

            if not self.usesharps:
                tmp = tmp[1::]
            if self.usequotes:
                tmp = f'"{tmp}"'

            data = f"{tmp}".join(data)

        with open(self.configfilepath, "w") as result:
            result.write(data)

        self.execute()

    def execute(self) -> None:
        if self.executeAfter != None:
            os.popen(self.executeAfter)


def read_templates() -> list[Template]:
    res: list[Template] = []

    with open(CONFIG.template_config_dir) as file:
        json_data = json.loads(file.read())

    for raw_template in json_data["templates"]:
        template = Template(
            templatepath=f'{HOME}/{raw_template["template_path"][2::]}'
            if raw_template["template_path"][0] == "~"
            else raw_template["template_path"],
            configfilepath=f'{HOME}/{raw_template["config_path"][2::]}'
            if raw_template["config_path"][0] == "~"
            else raw_template["config_path"],
            usequotes=raw_template["use_quotes"],
            usesharps=raw_template["use_sharps"],
            opacity=raw_template["opacity"] if raw_template["opacity"] != 0 else "",
            command=raw_template["command"],
        )
        res.append(template)

    return res


def read_displays() -> list[Display]:
    res: list[Display] = []

    for display in CONFIG.raw_displays_params:
        tmp = Display(
            name=display["name"],
            width=display["width"],
            height=display["height"],
            margin_x=display["margin-left"],
            margin_y=display["margin-right"],
        )
        res.append(tmp)

    return res


def resize_displays(displays: list[Display], image: Image) -> list[Display]:
    width, height = image.size
    max_width = Display.max_width(displays)

    width_dif = width / max_width

    for display in displays:
        display.w = int(display.w * width_dif)
        display.h = int(display.h * width_dif)
        display.x = int(display.x * width_dif)
        display.y = int(display.y * width_dif)

    max_height = Display.max_height(displays)
    height_dif = height / max_height

    if height_dif < 1:
        for display in displays:
            display.w = int(display.w * height_dif)
            display.h = int(display.h * height_dif)
            display.x = int(display.x * height_dif)
            display.y = int(display.y * height_dif)

    return displays


def resize_wallpaper(displays: list[Display], image: Image) -> Image:
    width, height = image.size
    max_width = Display.max_width(displays)

    width_dif: float = max_width / width

    new_width = int(width * width_dif)
    new_heigth = int(height * width_dif)

    image = image.resize((new_width, new_heigth))

    max_height = Display.max_height(displays)
    width, height = image.size
    height_dif = max_height / height

    if height_dif > 1:
        new_width = int(width * height_dif)
        new_heigth = int(height * height_dif)
        image = image.resize((new_width, new_heigth))

    return image


def split_wallpaper(displays: list[Display], image: Image) -> list[Display]:
    for display in displays:
        display.image = image.crop(
            (display.x, display.y, display.w + display.x, display.h + display.y)
        )

    return displays


def cache_wallpaper(wallpaper_name: str) -> None:
    wallpaper_name = (
        wallpaper_name.split("/")[-1] if "/" in wallpaper_name else wallpaper_name
    )
    wallpaper_name = (
        wallpaper_name.split("\n")[0] if "\n" in wallpaper_name else wallpaper_name
    )

    cache_is_needed = False

    for display in read_displays():
        if not os.path.exists(
            f'{CONFIG.cached_wallpapers_dir}/{display.name}-{display.w}.{display.h}.{display.x}.{display.y}{wallpaper_name.split('.')[0]}.png'
        ):
            cache_is_needed = True
            break

    if not cache_is_needed:
        return

    displays: list[Display] = read_displays()
    image: Image = Image.open(f"{CONFIG.wallpapers_dir}/{wallpaper_name}")

    if CONFIG.resize_displays:
        displays = resize_displays(displays, image)
    else:
        image = resize_wallpaper(displays, image)

    displays = split_wallpaper(displays, image)

    for display in displays:
        display.image.save(
            f'{CONFIG.cached_wallpapers_dir}/{display.name}-{display.w}.{display.h}.{display.x}.{display.y}{wallpaper_name.split('.')[0]}.png',
            optimize=True,
            quality=100,
        )


def set_wallpapper(wallpaper_name: str) -> None:
    displays: list[Display] = read_displays()
    templates: list[Template] = read_templates()
    wallpaper_name: str = f"{CONFIG.wallpapers_dir}/{wallpaper_name}"

    if "\n" in wallpaper_name:
        wallpaper_name = wallpaper_name[::-1][1::][::-1]
    pywal_command: str = f"python -m pywal -n -e -q {'-l' if CONFIG.light_theme else ''} {"-b " + CONFIG.wal_bg_color if CONFIG.wal_bg_color else ""} -i {wallpaper_name} --backend {CONFIG.wal_backend} "

    os.system(pywal_command)

    for display in displays:
        xorg = False

        try:
            if "wayland" in os.environ["XDG_BACKEND"]:
                os.system(
                    f"swww img {CONFIG.cached_wallpapers_dir}/{display.name}-{display.w}.{display.h}.{display.x}.{display.y}{wallpaperName.split('.')[0]}.png -o {display.name} {CONFIG.swww_params}"
                )

        except Exception as e:
            os.system(
                f"feh --bg-fill {CONFIG.wallpapers_dir}/{wallpaperName} --no-xinerama"
            )
            xorg = True

        if xorg:
            break

    with open(f"{CONFIG.wal_colors_dir}") as file:
        colors = (file.read()).split("\n")

    for template in templates:
        template.apply(colors)


def main(wallpaperName: str, runcount: int = -1) -> None:
    iteration = 0
    prev_wallpaper = None

    try:
        while iteration != runcount:
            if iteration > 0:
                time.sleep(CONFIG.sleep_time)
            while wallpaperName == prev_wallpaper:
                wallpaperName = random.choice(os.listdir(CONFIG.wallpapers_dir))
            prev_wallpaper = wallpaperName

            cache_wallpaper(wallpaperName)
            set_wallpapper(wallpaperName)

            iteration += 1

    except KeyboardInterrupt:
        print("exiting...")
        return


if __name__ == "__main__":
    runcount, wallpaperName = CONFIG.read_args()
    main(wallpaperName=wallpaperName, runcount=runcount)
