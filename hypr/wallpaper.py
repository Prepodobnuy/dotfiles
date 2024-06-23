# requirements:
# pywal
# for xorg wallpaper change
# feh 
# for wayland wallpaper change
# pillow
# swww

import os
import sys
import time
import random
import subprocess

from PIL import Image


HOME = os.getenv("HOME")
WALLPAPERSDIR = f"{HOME}/Documents/Wallpapers"
WALCOLORSPATH = f"{HOME}/.cache/wal/colors"
WALBACKEND = f"colorz"
CACHEDWALLPAPERSDIR = f"{HOME}/Documents/CachedWallpapers"
WORKINGDIR = f"{HOME}/.config/hypr"
SWWWPARAMS = "--transition-fps 165 -t any"
SLEEPTIME = 360000
HELPMESSAGE = """-h --help                      display this message
-p [path]                      set wallpapers directory
-w [backend]                   set wal backend
-s [value]                     set sleep time
--dconf [path]                 set display config path
--swww "-param --param 123"    set swww params"""

class display(object):
    def __init__(self, name:str, width:int, height:int, margin_x:int=0, margin_y:int=0) -> None:
        self.name:str = name
        self.w:int = width
        self.h:int = height
        self.x:int = margin_x
        self.y:int = margin_y
        
        self.image = None
    
    def __str__(self) -> str:
        return f"{self.name} {self.w}x{self.h} {self.x}x{self.y}"
    def __repr__(self) -> str:
        return f"{self.name} {self.w}x{self.h} {self.x}x{self.y}"

class template(object):
    def __init__(self, templatepath, configpath, usequotes=False, usesharps=False, command=None, opacity='') -> None:
        self.templatefilepath = templatepath
        self.configfilepath = configpath
        self.executeAfter = command
        self.usequotes = usequotes
        self.usesharps = usesharps
        self.opacity = opacity

    def __str__(self) -> str:
        return f"Command: {self.executeAfter} {self.templatefilepath} -> {self.configfilepath};"
    
    def __repr__(self) -> str:
        return f"Command: {self.executeAfter} {self.templatefilepath} -> {self.configfilepath};"

    def apply_colors(self, colors) -> None:
        with open(self.templatefilepath, 'r') as template:
            data = template.read()
            
        for num, color in enumerate(colors):
            data = data.split(f'(color{num})')
            tmp = color + self.opacity
            if not self.usesharps:
                tmp = tmp[1::]
            if self.usequotes:
                tmp = f'"{tmp}"'
            data = f'{tmp}'.join(data)
            
        with open(self.configfilepath, 'w') as result:
            result.write(data)
        
        self.execute()

    def execute(self):
        if self.executeAfter != None:
            os.popen(self.executeAfter)

def runrofi(wallpapers):
    result = subprocess.run(['rofi', '-dmenu', '-p'], input='\n'.join(wallpapers).encode(), stdout=subprocess.PIPE)
    return result.stdout.decode()

def max_width(displays:list[display]):
    res = 0
    for display in displays:
        res = display.w + display.x if display.w + display.x > res else res
    
    return res

def max_height(displays:list[display]):
    res = 0
    for display in displays:
        res = display.h + display.y if display.h + display.y > res else res
    
    return res

def read_display_config() -> list[display]:
    res:list[display] = []
    with open(f"{WORKINGDIR}/displays") as file:
        data = (file.read()).split('\n')

    for row in data:
        params = row.split('=')[1].split(',')
        tmp = display(
            name=params[0],
            width=int(params[1].split('x')[0]),
            height=int(params[1].split('x')[1]),
            margin_x=int(params[2].split('x')[0]),
            margin_y=int(params[2].split('x')[1])
        )
        res.append(tmp)

    return res

def resize_displays(displays:list[display], wallpaper_path:str):
    #print("//resizing displays")
    maxw = max_width(displays)
    maxh = max_height(displays)

    image = Image.open(wallpaper_path)
    imagew, imageh = image.size

    width_dif = imagew / maxw
    height_dif = imageh / maxh

    for display in displays:
        display.w = int(display.w * width_dif)
        display.h = int(display.h * width_dif)
        display.x = int(display.x * width_dif)
        display.y = int(display.y * width_dif)

    #print(f"default params:\n\timage {imagew}x{imageh}\n\tdispays {maxw}x{maxh}\n\tdifference {width_dif}x{height_dif}")

    maxw = max_width(displays)
    maxh = max_height(displays)
    width_dif = imagew / maxw
    height_dif = imageh / maxh
    #print(f"after width scaling:\n\timage {imagew}x{imageh}\n\tdispays {maxw}x{maxh}\n\tdifference {width_dif}x{height_dif}")

    if height_dif < 1:
        for display in displays:
            display.w = int(display.w * height_dif)
            display.h = int(display.h * height_dif)
            display.x = int(display.x * height_dif)
            display.y = int(display.y * height_dif)

    maxw = max_width(displays)
    maxh = max_height(displays)
    width_dif = imagew / maxw
    height_dif = imageh / maxh
    #print(f"after height scaling:\n\timage {imagew}x{imageh}\n\tdispays {maxw}x{maxh}\n\tdifference {width_dif}x{height_dif}")

    return displays

def split_wallpaper(displays, wallpaper):
    #print("//spliting image")
    image = Image.open(wallpaper)

    for display in displays:
        display.image = image.crop((
            display.x,
            display.y,
            display.w + display.x,
            display.h + display.y 
        ))
        #print(f"image: {display.x}x{display.y} {display.w + display.x}x{display.h + display.y}")
    
    return displays

def cacheWallpapers():
    for wallpaperName in os.listdir(WALLPAPERSDIR):
        wallpaper = f"{WALLPAPERSDIR}/{wallpaperName}" 
        displays = resize_displays(read_display_config(), wallpaper)
        displays = split_wallpaper(displays, wallpaper)
        print(f"caching {wallpaperName}...")
        for display in displays:
            if os.path.exists(f'{CACHEDWALLPAPERSDIR}/{display.name}{wallpaperName.split('.')[0]}.png'): 
                print(f"{wallpaperName} is already cached")
                break
            else: display.image.save(f'{CACHEDWALLPAPERSDIR}/{display.name}{wallpaperName.split('.')[0]}.png', optimize=True, quality=100)

    print()

def read_templates():
    res = []
    with open(f"{WORKINGDIR}/configs") as file:
        data = (file.read()).split('\n')
    
    for row in data:
        tmpdata = row.split(';')
        try:
            commanddata = ';'.join(tmpdata[5::])
            temp = template(
                templatepath=tmpdata[0],
                configpath=tmpdata[1],
                usequotes=True if '1' in tmpdata[2] else False,
                usesharps=True if '1' in tmpdata[3] else False,
                opacity=tmpdata[4] if not '0' in tmpdata[4] else '',
                command=commanddata
            )
        except Exception:
            temp = template(
                templatepath=tmpdata[0],
                configpath=tmpdata[1],
                usequotes=True if '1' in tmpdata[2] else False,
                usesharps=True if '1' in tmpdata[3] else False,
                opacity=tmpdata[4] if not '0' in tmpdata[4] else ''
            )

        res.append(temp)

    return res

def main(wallpaperName):
    wallpaper = f"{WALLPAPERSDIR}/{wallpaperName}" 
    
    os.system(f"python -m pywal -i {wallpaper} -n --backend {WALBACKEND}")
    print(f"\n//selected image: {wallpaper}")
    
    try:
        if 'wayland' in os.environ['XDG_BACKEND']:
            displays = read_display_config()
            print('//splited to:')
            for display in displays:
                print(f"{CACHEDWALLPAPERSDIR}/{display.name}{wallpaperName.split('.')[0]}.png")
                os.system(f"swww img {CACHEDWALLPAPERSDIR}/{display.name}{wallpaperName.split('.')[0]}.png -o {display.name} {SWWWPARAMS}")
    except Exception as e:
        print(e)
        os.system(f"feh --bg-fill --no-xinerama {WALLPAPERSDIR}/{wallpaperName}")

    templates = read_templates()
    with open(f'{WALCOLORSPATH}') as file:
        colors = (file.read()).split('\n')

    print("\n//changing configs:")
    for template in templates:
        print(template)
        template.apply_colors(colors)

if __name__ == "__main__":
    args = sys.argv

    if '-h' in args or '--help' in args:
        print(HELPMESSAGE)
        exit()

    if '-p' in args: WALLPAPERSDIR = args[args.index('-p')+1]
    if '-w' in args: WALBACKEND = args[args.index('-w')+1]
    if '-s' in args: SLEEPTIME = int(args[args.index('-s')+1])
    if '--dconf' in args: WORKINGDIR = args[args.index('--dconf')+1]
    if '--swww' in args: SWWWPARAMS = args[args.index('--swww')+1]
    if '-r' in args: 
        tmp = runrofi(os.listdir(WALLPAPERSDIR))
        main(tmp)         
    else:
        try:
            wallpapers = os.listdir(WALLPAPERSDIR)
            cacheWallpapers()
            while True:
                tmp, wallpaper = "lol", "lol"

                while wallpaper == tmp:
                    wallpaperName = random.choice(wallpapers)
                    wallpaper = f"{WALLPAPERSDIR}/{wallpaperName}" 
                tmp = wallpaper

                main(wallpaperName)

                if '--once' in args:
                    time.sleep(2)
                    exit()

                time.sleep(SLEEPTIME)

        except KeyboardInterrupt:
            print("exiting")
            exit()
