from cx_Freeze import setup, Executable

exe = Executable(
     script="main.py",
     base="Win32Gui",
     icon="E:\\Python\\Fun Marathon\\resources\\dsicon.ico",
     shortcutName = "Fun Marathon",
     shortcutDir = "DesktopFolder"
     )

exe2 = Executable(
     script="main.py",
     base="Win32Gui",
     icon="E:\\Python\\Fun Marathon\\resources\\dsicon.ico",
     shortcutName = "Fun Marathon",
     shortcutDir = "StartMenuFolder"
     )

setup(
     version = "1.0",
     description = "An application to show when your FDs are matured and help you save time.",
     author = "Dhruv Somani",
     name = "FD Storage",
     options = {'build_exe': {'packages':['tkinter', 'tkinter.ttk', 'tkinter.tix', 'tkinter.messagebox',
                                          'tkinter.colorchooser', 'tkinter.filedialog', 'sqlite3',
                                          'os', 'PIL', 'objects', 'widgets']}},
     executables = [exe, exe2]
     )
