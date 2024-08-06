import os
import random

def main():
    wallpaper = random.choice(os.listdir(f'{os.getenv("HOME")}/Documents/Wallpapers'))
    
    os.system(f'rpaper {os.path.abspath(f"{os.getenv('HOME')}/Documents/Wallpapers/{wallpaper}")}')


if __name__ == "__main__":
    main()