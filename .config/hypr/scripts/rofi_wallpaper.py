import os
import random
import subprocess


def runrofi(wallpapers) -> list[str]:
        result = subprocess.run(
            ["rofi", "-dmenu", "-p"],
            input="\n".join(wallpapers).encode(),
            stdout=subprocess.PIPE,
        )

        if '\n' in result.stdout.decode():
            return result.stdout.decode()[::-1][1::][::-1]
        return result.stdout.decode()
        
def main():
    wallpaper = runrofi(os.listdir(f'{os.getenv("HOME")}/Documents/Wallpapers'))
    
    os.system(f'rpaper {os.path.abspath(f"{os.getenv('HOME')}/Documents/Wallpapers/{wallpaper}")}')


if __name__ == "__main__":
    main()