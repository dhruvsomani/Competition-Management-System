# Fun-Marathon
This repository contains the source code for a software, Fun Marathon which is designed to host and manage scores of many games which are
played by the same individuals or teams.

First of all, **the software is in beta**. If you are trying to use it for your own personal purposes, you're responsible for it.
Changes, suggestions and edits are welcome.

The software has an issue which will be solved in future versions. Add you players to it manually in the **SQLite Database (Table Players)**.
I hope to resolve this fallacy in later editions of the software.

An executable file will be available soon.

## main.py
This file contains the main code which will run on execution. Run this file.

## objects.py
This file contains the class `Game` which represents a singular game (*not a set of games*) and also a `tkinter.frame` which will be
inserted in the `tkinter.ttk.Notebook` in the `main.py`.
It also contains the class `Settings` which represents a single settings window for changing the settings.

## sanitize.py
This file contains a single function to help recognize data and insert it into the database accordingly. It scrapes the data from a file.

I welcome suggestions which may help make the applicaton better. Thanks!
