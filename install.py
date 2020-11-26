import os
windows = os.name == 'nt'
python = input("Python3 are installed as (python/python3): ")
os.system(f"{python} -m pip install -r requirements.txt")
if not windows:
    os.system('mkdir /usr/share/imagehacker')
    os.system('cp -r * /usr/share/imagehacker')
    os.system('ln -s /usr/share/imagehacker/imagehacker.py /usr/bin/imagehacker')
else:
    os.system("mkdir C:\\imagehacker")
    os.system("copy * C:\\imagehacker")
    os.system("mkdir C:\\imagehacker\\include")
    os.system("copy include C:\\imagehacker\\include\\")
    os.system("echo @echo off > C:\\Windows\\System32\\imagehacker.bat")
    os.system(f"echo {python} C:\\imagehacker\\imagehacker.py %* >> C:\\Windows\\System32\\imagehacker.bat")

print("[+]ImageHacker installed!")
