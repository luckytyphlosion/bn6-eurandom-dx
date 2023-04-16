import subprocess
import sys

def main():
    start_index = int(sys.argv[1])

    for i in range(start_index, 31):
        subprocess.run(["python3", "gen_folder.py", "-o", f"good_folders/temp{i}.txt"], check=True)

    subprocess.run(["python3", "gen_folder.py", "-o", "temp31.txt", "-p"], check=True)

if __name__ == "__main__":
    main()
