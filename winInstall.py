#!/usr/bin/env python3
from sys import version_info,executable,platform
import subprocess

def installManual(URL):
    subprocess.check_call([executable, "-m", "pip", "install", URL])


def installRest():
    subprocess.check_call([executable, "-m", "pip", "install", "."])

if __name__ == "__main__":
    ver =f"cp{version_info[0]}{version_info[1]}"

    if platform == 'win32' or platform =='amd64':
        traitsURL = f"https://download.lfd.uci.edu/pythonlibs/w3jqiv8s/traits-6.1.1-{ver}-{ver}-{platform}.whl"
        vtkURL = f"https://download.lfd.uci.edu/pythonlibs/w3jqiv8s/VTK-9.0.1-{ver}-{ver}-{platform}.whl"
        installManual(traitsURL)
        installManual(vtkURL)
    installRest()