# requirements:
# pywal
# colorz
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
WALLPAPERSDIR = f"{HOME}/Documents/Wallpapers"                 #-wd --wallpaper-dir [path/to/dir]
CACHEDWALLPAPERSDIR = f"{HOME}/Documents/CachedWallpapers"     #-cwd --cached-wallpaper-dir [path/to/dir]
WALCOLORSDIR = f"{HOME}/.cache/wal/colors"                     #-pcd --pywal-colors-dir [path/to/dir]
WALBACKEND = f"colorz"                                         #-pb --pywal-backend [backed]
CONFIGPATH = f"{HOME}/.config/hypr/configs"                    #-c --conf [path/to/file]
DISPLAYPATH = f"{HOME}/.config/hypr/displays"                  #-dc --display-conf [path/to/file] 
SWWWPARAMS = "--transition-fps 165 -t any"                     #--swww "-param -param"
SLEEPTIME = 360000                                             #-s --sleep-time timeToSleepInSeconds
RESIZEDISPLAYS = False                                         #--resize-displays
HELPMESSAGE = """-wd --wallpaper-dir [path/to/dir]
-cwd --cached-wallpaper-dir [path/to/dir]
-pcd --pywal-colors-dir [path/to/dir]
-pb --pywal-backend [backed]
-c --conf [path/to/file]
-dc --display-conf [path/to/file] 
--swww "-param -param"
-s --sleep-time timeToSleepInSeconds
--resize-displays
--cache-all
"""
DEBUG = False

class Display(object):
    def __init__(self, name:str, width:int, height:int, margin_x:int=0, margin_y:int=0) -> None:
        self.name:str = name
        self.w:int = width
        self.h:int = height
        self.x:int = margin_x
        self.y:int = margin_y    
        self.image = None

    def max_width(displays:list) -> int:
        res = 0
        for display in displays:
            res = display.w + display.x if display.w + display.x > res else res
        return res

    def max_height(displays:list) -> int:
        res = 0
        for display in displays:
            res = display.h + display.y if display.h + display.y > res else res
        return res
    
    def __str__(self) -> str:
        return f"{self.name} {self.w}x{self.h} {self.x}x{self.y}"
    
    def __repr__(self) -> str:
        return f"{self.name} {self.w}x{self.h} {self.x}x{self.y}"

def read_display_config() -> list[Display]:
    res:list[Display] = []
    with open(DISPLAYPATH) as file:
        data = (file.read()).split('\n')

    for row in data:
        if row == '': continue
        if row[0] == '#': continue
        params = row.split('=')[1].split(',')
        tmp = Display(
            name=params[0],
            width    = int(params[1].split('x')[0]),
            height   = int(params[1].split('x')[1]),
            margin_x = int(params[2].split('x')[0]),
            margin_y = int(params[2].split('x')[1])
        )
        res.append(tmp)
    return res

def resize_displays(displays:list[Display], wallpaper:Image):
    if DEBUG: print("//resizing displays")
    maxw = Display.max_width(displays)
    imagew, imageh = wallpaper.size
    width_dif = imagew / maxw

    for display in displays:
        display.w = int(display.w * width_dif)
        display.h = int(display.h * width_dif)
        display.x = int(display.x * width_dif)
        display.y = int(display.y * width_dif)


    maxh = Display.max_height(displays)
    height_dif = imageh / maxh

    if height_dif < 1:
        for display in displays:
            display.w = int(display.w * height_dif)
            display.h = int(display.h * height_dif)
            display.x = int(display.x * height_dif)
            display.y = int(display.y * height_dif)

    return displays

def resize_wallpaper(displays:list[Display], wallpaper:Image):
    if DEBUG: print("//resizing picture")
    maxw = Display.max_width(displays)
    imagew, imageh = wallpaper.size

    width_dif =  maxw / imagew

    nwidth  = int(imagew * width_dif)
    nheigth = int(imageh * width_dif)

    wallpaper = wallpaper.resize((nwidth, nheigth))

    maxh = Display.max_height(displays)
    imagew, imageh = wallpaper.size
    height_dif = maxh / imageh

    if height_dif > 1:
        nwidth  = int(imagew * height_dif)
        nheigth = int(imageh * height_dif)
        wallpaper = wallpaper.resize((nwidth, nheigth))
    
    return wallpaper

def split_wallpaper(displays, wallpaper):
    if DEBUG: print("//spliting image")
    for display in displays:
        display.image = wallpaper.crop((
            display.x,
            display.y,
            display.w + display.x,
            display.h + display.y 
        ))
        if DEBUG: print(f"image: {display.x}x{display.y} {display.w + display.x}x{display.h + display.y}")
    
    return displays

class Template(object):
    def __init__(self, templatepath, configpath, usequotes=False, usesharps=False, command=None, opacity='') -> None:
        self.templatefilepath = templatepath
        self.configfilepath = configpath
        self.executeAfter = command
        self.usequotes = usequotes
        self.usesharps = usesharps
        self.opacity = opacity

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

    def __str__(self) -> str:
        return f"Command: {self.executeAfter} {self.templatefilepath} -> {self.configfilepath};"
    
    def __repr__(self) -> str:
        return f"Command: {self.executeAfter} {self.templatefilepath} -> {self.configfilepath};"

def read_templates():
    res = []
    with open(CONFIGPATH) as file:
        data = (file.read()).split('\n')
    
    for row in data:
        if row == '': continue
        if row[0] == '#': continue
        tmpdata = row.split(';')
        try:
            commanddata = ';'.join(tmpdata[5::])
            temp = Template(
                templatepath=tmpdata[0],
                configpath=tmpdata[1],
                usequotes='1' in tmpdata[2],
                usesharps='1' in tmpdata[3],
                opacity=tmpdata[4] if not '0' in tmpdata[4] else '',
                command=commanddata
            )
        except IndexError:
            temp = Template(
                templatepath=tmpdata[0],
                configpath=tmpdata[1],
                usequotes='1' in tmpdata[2],
                usesharps='1' in tmpdata[3],
                opacity=tmpdata[4] if not '0' in tmpdata[4] else ''
            )

        res.append(temp)

    return res

def runrofi(wallpapers):
    result = subprocess.run(['rofi', '-dmenu', '-p'], input='\n'.join(wallpapers).encode(), stdout=subprocess.PIPE)
    return result.stdout.decode()

def cacheWallpapers(image=None):
    def cache(wallpaperName):
        default_displays = read_display_config()
        print(f"caching {wallpaperName}...")
        for i in range(len(default_displays)):
            if os.path.exists(f'{CACHEDWALLPAPERSDIR}/{default_displays[i].name}-{default_displays[i].w}.{default_displays[i].h}.{default_displays[i].x}.{default_displays[i].y}{wallpaperName.split('.')[0]}.png'): 
                print(f"image for {default_displays[i].name} is already cached")
                continue

            wallpaper = Image.open(f"{WALLPAPERSDIR}/{wallpaperName}") 
            if RESIZEDISPLAYS: displays = resize_displays(read_display_config(), wallpaper)
            else: 
                displays = read_display_config()
                wallpaper = resize_wallpaper(displays, wallpaper)

            displays = split_wallpaper(displays, wallpaper)
            displays[i].image.save(f'{CACHEDWALLPAPERSDIR}/{default_displays[i].name}-{default_displays[i].w}.{default_displays[i].h}.{default_displays[i].x}.{default_displays[i].y}{wallpaperName.split('.')[0]}.png', optimize=True, quality=100)
        print("-------------------------------------")

    if image == None:
        for wallpaperName in os.listdir(WALLPAPERSDIR):
            cache(wallpaperName)
    else: 
        wallpaperName = image.split('/')[-1] if '/' in image else image
        wallpaperName = wallpaperName.split('\n')[0] if '\n' in wallpaperName else wallpaperName
        cache(wallpaperName)
    print()

def set_wallpapper(wallpaperName):
    displays = read_display_config()
    for display in displays:
        wallpaper = f"{WALLPAPERSDIR}/{wallpaperName}" 
        xorg = False
        os.system(f"python -m pywal -i {wallpaper} -n --backend {WALBACKEND}")
        print(f"\n//selected image: {wallpaper}")
        
        try:
            if 'wayland' in os.environ['XDG_BACKEND']:
                print('//splited to:')
                print(f"{CACHEDWALLPAPERSDIR}/{display.name}-{display.w}.{display.h}.{display.x}.{display.y}{wallpaperName.split('.')[0]}.png")
                os.system(f"swww img {CACHEDWALLPAPERSDIR}/{display.name}-{display.w}.{display.h}.{display.x}.{display.y}{wallpaperName.split('.')[0]}.png -o {display.name} {SWWWPARAMS}")
        
        except Exception as e:
            print(e)
            os.system(f"feh --bg-fill {WALLPAPERSDIR}/{wallpaperName} --no-xinerama")
            xorg = True
        templates = read_templates()
        with open(f'{WALCOLORSDIR}') as file:
            colors = (file.read()).split('\n')
        print("\n//changing configs:")
        for template in templates:
            print(template)
            template.apply_colors(colors)
        if xorg: break


def main(wallpaperName, runcount=None) -> None:
    iteration = 0
    prev_wallpaper = None

    try:
        while iteration != runcount:
            if iteration > 0 : time.sleep(SLEEPTIME)
            while wallpaperName == prev_wallpaper:
                wallpaperName = random.choice(os.listdir(WALLPAPERSDIR))
            prev_wallpaper = wallpaperName

            cacheWallpapers(wallpaperName)
            set_wallpapper(wallpaperName)
            
            iteration += 1
    except KeyboardInterrupt:
        print('exiting...')
        return

def in_args(params:list[str]) -> bool:
    for param in params:
        if param in sys.argv: return True
    return False

def get_value_from_args(params:list[str]) -> str:
    for param in params:
        if param in sys.argv: return  sys.argv[sys.argv.index(param)+1]
    return None

if __name__ == "__main__":
    wallpaperName=random.choice(os.listdir(WALLPAPERSDIR))
    runcount = -1


    if in_args(['-h', '--help']): print(HELPMESSAGE); exit()
    if in_args(['-wd', '--wallpaper-dir']):         WALLPAPERSDIR       = get_value_from_args(['-wd', '--wallpaper-dir'])
    if in_args(['-cwd', '--cached-wallpaper-dir']): CACHEDWALLPAPERSDIR = get_value_from_args(['-cwd', '--cached-wallpaper-dir'])
    if in_args(['-pcd', '--pywal-colors-dir']):     WALCOLORSDIR        = get_value_from_args(['-pcd', '--pywal-colors-dir'])
    if in_args(['-pb', '--pywal-backend']):         WALBACKEND          = get_value_from_args(['-pb', '--pywal-backend'])
    if in_args(['-c', '--conf']):                   CONFIGPATH          = get_value_from_args(['-c', '--conf'])
    if in_args(['-dc', '--display-conf']):          DISPLAYPATH         = get_value_from_args(['-dc', '--display-conf'])
    if in_args(['--swww']):                         SWWWPARAMS          = get_value_from_args(['--swww'])
    if in_args(['-s', '--sleep-time']):             SLEEPTIME       = int(get_value_from_args(['-s','--sleep-time']))
    if in_args(['--resize-displays']):              RESIZEDISPLAYS = True
    if in_args(['--cache-all']): cacheWallpapers()
    if in_args(['-r', '--rofi']): 
        wallpaperName = runrofi(os.listdir(WALLPAPERSDIR))
        runcount = 1 
    if in_args(['--once']): 
        runcount = 1
    
    main(
        wallpaperName=wallpaperName, 
        runcount=runcount
        )