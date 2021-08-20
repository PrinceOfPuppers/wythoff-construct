def main():
    print("Welcome to Wythoff Construct")
    print("Loading Dependancies...")
    from wythoff_construct.ui import Ui
    print("Loading UI...")
    ui = Ui()
    print("Done")

    ui.configure_traits()