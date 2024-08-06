import os

def main():
    wallpapers = os.listdir(f'{os.getenv("HOME")}/Documents/Wallpapers')
    for wallpaper in wallpapers:
        os.system(f'rpaper_cache {os.path.abspath(f"{os.getenv('HOME')}/Documents/Wallpapers/{wallpaper}")}')


if __name__ == "__main__":
    main()