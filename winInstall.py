#!/usr/bin/env python3
from sys import version_info,executable,platform
import subprocess

def installManual(URL):
    subprocess.check_call([executable, "-m", "pip", "install", URL])


def installRest():
    for package in ['numpy','scipy','PyQt5',"mayavi"]:
        subprocess.check_call([executable, "-m", "pip", "install",package])


if __name__ == "__main__":
    ver =f"cp{version_info[0]}{version_info[1]}"

    if platform == 'win32' or platform =='amd64':
        traitsURL = f"https://download.lfd.uci.edu/pythonlibs/x2tqcw5k/traits-6.1.1-{ver}-{ver}-{platform}.whl"
        vtkURL = f"https://download.lfd.uci.edu/pythonlibs/x2tqcw5k/VTK-9.0.1-{ver}-{ver}-{platform}.whl"
        installManual(traitsURL)
        installManual(vtkURL)
        installRest()