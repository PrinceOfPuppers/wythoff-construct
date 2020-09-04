#!/usr/bin/env python3
if __name__ == "__main__":
    print("Welcome to Wythoff Construct")
    print("Loading Dependancies...")
    from project.ui import Ui
    ui = Ui()

    ui.configure_traits()