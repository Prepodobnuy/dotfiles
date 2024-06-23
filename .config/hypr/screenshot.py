import os
import subprocess


def main():
    process = subprocess.run(['hyprshotgun', 'region'], stdout=subprocess.PIPE)
    output = process.stdout.strip().decode()
    
    os.system(f'wl-copy < {output}')
    os.remove(output)

if __name__ == "__main__":
    main()