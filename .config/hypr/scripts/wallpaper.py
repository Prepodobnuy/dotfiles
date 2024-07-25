import os
import sys
import time
import random
import subprocess
import json

from PIL import Image

HOME = os.getenv("HOME")
WALLPAPERSDIR = f"{HOME}/Documents/Wallpapers"                 #-wd --wallpaper-dir [path/to/dir]
CACHEDWALLPAPERSDIR = f"{HOME}/Documents/CachedWallpapers"     #-cwd --cached-wallpaper-dir [path/to/dir]
WALCOLORSDIR = f"{HOME}/.cache/wal/colors"                     #-pcd --pywal-colors-dir [path/to/dir]
WALBACKEND = f"colorz"                                         #-pb --pywal-backend [backed]
WALBACKGROUNDCOLOR = ""                                        #-pbc --pywal-backgroundcolor [color]
CONFIGPATH = f"{HOME}/.config/hypr/scripts/templates.json"     #-c --conf [path/to/file]
NOTJSONCONFIG = False                                          # not json configs is deprecated
DISPLAYPATH = f"{HOME}/.config/hypr/scripts/displays"          #-dc --display-conf [path/to/file] 
SWWWPARAMS = "--transition-fps 165 -t any"                     #--swww "-param -param"
SLEEPTIME = 360000                                             #-s --sleep-time timeToSleepInSeconds
RESIZEDISPLAYS = False                                         #--resize-displays
LIGHTTHEME = False                                             #-l --light
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
        print_if_debug("//Display __init__ method called")
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

    def max_width(displays:list) -> int:
        print_if_debug("//Display max_width method called")
        res = 0
        for display in displays:
            res = display.w + display.x if display.w + display.x > res else res
        return res

    def max_height(displays:list) -> int:
        print_if_debug("//Display max_height method called")
        res = 0
        for display in displays:
            res = display.h + display.y if display.h + display.y > res else res
        return res

class Template(object):
    def __init__(self, templatepath, configpath, usequotes=False, usesharps=False, command=None, opacity='') -> None:
        print_if_debug("//Template __init__ method called")
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

    def apply(self, colors:list[str]) -> None:
        print_if_debug("//Template apply method called")
        print_if_debug(f"from: {self.templatefilepath}")
        print_if_debug(f"  to: {self.configfilepath}")
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

    def execute(self) -> None:
        print_if_debug("//Template execute method called")
        if self.executeAfter != None:
            print_if_debug(f"command:{self.executeAfter}")
            os.popen(self.executeAfter)

def print_if_debug(string:str) -> None:
    if DEBUG: print(string)

def read_display_config() -> list[Display]:
    print_if_debug("//read_display_config def called")
    res:list[Display] = []

    with open(DISPLAYPATH) as file:
        data = file.read().split('\n')

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

def read_templates() -> list[Template]:
    print_if_debug("//read_templates def called")
    with open(CONFIGPATH) as file:
        json_data = json.loads(file.read())

    res:list[Template] = []

    for raw_template in json_data["templates"]:
        print(raw_template)

        template = Template(
            templatepath= f'{HOME}/{raw_template["template_path"][2::]}' if raw_template["template_path"][0] == '~' else raw_template["template_path"],
            configpath= f'{HOME}/{raw_template["config_path"][2::]}' if raw_template["config_path"][0] == '~' else raw_template["config_path"],
            usequotes= raw_template["use_quotes"],
            usesharps= raw_template["use_sharps"],
            opacity= raw_template["opacity"] if raw_template["opacity"] != 0 else '',
            command= raw_template["command"]
        )
        res.append(template)

    return res

def resize_displays(displays:list[Display], wallpaper:Image) -> list[Display]:
    print_if_debug("//resize_displays def called")
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

def resize_wallpaper(displays:list[Display], wallpaper:Image) -> Image:
    print_if_debug("//resize_wallpaper def called")
    maxw:int = Display.max_width(displays)
    imagew, imageh = wallpaper.size

    width_dif:float =  maxw / imagew

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
    print_if_debug("//split_wallpaper def called")
    for display in displays:
        display.image = wallpaper.crop((
            display.x,
            display.y,
            display.w + display.x,
            display.h + display.y 
        ))
        print_if_debug(f"image: {display.x}x{display.y} {display.w + display.x}x{display.h + display.y}")
    
    return displays

def cacheWallpapers(image=None):
    print_if_debug("//cacheWallpapers def called")
    def cache(wallpaperName):
        default_displays = read_display_config()
        print_if_debug(f"caching {wallpaperName}...")
        for i in range(len(default_displays)):
            if os.path.exists(f'{CACHEDWALLPAPERSDIR}/{default_displays[i].name}-{default_displays[i].w}.{default_displays[i].h}.{default_displays[i].x}.{default_displays[i].y}{wallpaperName.split('.')[0]}.png'): 
                print_if_debug(f"image for {default_displays[i].name} is already cached")
                continue

            wallpaper = Image.open(f"{WALLPAPERSDIR}/{wallpaperName}") 
            if RESIZEDISPLAYS: displays = resize_displays(read_display_config(), wallpaper)
            else: 
                displays = read_display_config()
                wallpaper = resize_wallpaper(displays, wallpaper)

            displays = split_wallpaper(displays, wallpaper)
            displays[i].image.save(f'{CACHEDWALLPAPERSDIR}/{default_displays[i].name}-{default_displays[i].w}.{default_displays[i].h}.{default_displays[i].x}.{default_displays[i].y}{wallpaperName.split('.')[0]}.png', optimize=True, quality=100)

    if image == None:
        for wallpaperName in os.listdir(WALLPAPERSDIR):
            cache(wallpaperName)
    else: 
        wallpaperName = image.split('/')[-1] if '/' in image else image
        wallpaperName = wallpaperName.split('\n')[0] if '\n' in wallpaperName else wallpaperName
        cache(wallpaperName)

def set_wallpapper(wallpaperName:str) -> None:
    print_if_debug("//set_wallpapper def called")
    displays:list[Display]   = read_display_config()
    templates:list[Template] = read_templates()
    wallpaper:str     = f"{WALLPAPERSDIR}/{wallpaperName}" 

    if '\n' in wallpaper: wallpaper = wallpaper[::-1][1::][::-1]
    pywal_command:str = f"python -m pywal -n -e -q {'-l' if LIGHTTHEME else ''} {"-b " + WALBACKGROUNDCOLOR if WALBACKGROUNDCOLOR else ""} -i {wallpaper} --backend {WALBACKEND} "
    
    print_if_debug(f"\nselected image: {wallpaper}")
    os.system(pywal_command)

    for display in displays:
        xorg = False

        try:
            if 'wayland' in os.environ['XDG_BACKEND']:
                print_if_debug('splited to:')
                print_if_debug(f"{CACHEDWALLPAPERSDIR}/{display.name}-{display.w}.{display.h}.{display.x}.{display.y}{wallpaperName.split('.')[0]}.png")
                os.system(f"swww img {CACHEDWALLPAPERSDIR}/{display.name}-{display.w}.{display.h}.{display.x}.{display.y}{wallpaperName.split('.')[0]}.png -o {display.name} {SWWWPARAMS}")

        except Exception as e:
            print_if_debug(e)
            os.system(f"feh --bg-fill {WALLPAPERSDIR}/{wallpaperName} --no-xinerama")
            xorg = True

        if xorg: break
    
    with open(f'{WALCOLORSDIR}') as file:
        colors = (file.read()).split('\n')
    
    for template in templates:
        template.apply(colors)

def main(wallpaperName:str, runcount:int=-1) -> None:
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

def runrofi(wallpapers) -> list[str]:
    result = subprocess.run(['rofi', '-dmenu', '-p'], input='\n'.join(wallpapers).encode(), stdout=subprocess.PIPE)
    return result.stdout.decode()

def in_args(params:list[str]) -> bool:
    for param in params:
        if param in sys.argv: return True
    return False

def get_value_from_args(params:list[str]) -> str|None:
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
    if in_args(['-pbc', '--pywal-backgroundcolor']):WALBACKGROUNDCOLOR  = get_value_from_args(['-pbc', '--pywal-backgroundcolor'])
    if in_args(['-s', '--sleep-time']):             SLEEPTIME       = int(get_value_from_args(['-s','--sleep-time']))
    if in_args(['--resize-displays']):              RESIZEDISPLAYS      = True
    if in_args(['-l', '--light']):                  LIGHTTHEME          = True
    if in_args(['--once']):                         runcount = 1 
    if in_args(['--cache-all']): cacheWallpapers()
    if in_args(['-r', '--rofi']): 
        wallpaperName = runrofi(os.listdir(WALLPAPERSDIR))
        runcount = 1 
    main(
        wallpaperName=wallpaperName, 
        runcount=runcount
        )