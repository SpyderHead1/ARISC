# ARISC
Configuration tool for the ARIS dashboard

ARISC stands for Advanced Race Information System Configurator.
It is just a little helper to read, write, backup and restore the configuration files that are used by my ARIS dashboard for SimHub.

This small tool is written in Python 3.10 and uses the Kivy 2.1.0 framework as well as some small functions from Tkinter (the file chooser for the backup and restore funtionality). So you need Python 3.10 and Kivy 2.1.0 (and my ARIS dashboard for SimHub for sure) installed to run this little program.

- "ARIS configurator.py" contains almost the complete code
- "Custom.py" contains some customized classes that might be useful in other projects as well

Side note - I know I could have used the kv design language but this is my first python program and the very first time I got in touch with Kivy. So bear with me =)

And I know, it could be better commented. If I have some spare time I add some more comments to the code ;)

### Why version 3.x?
Version 1.0 completely used only Tkinter for the GUI. But at some point I ran in some problems with it, so I had to switch the GUI framework. Version 2.0 then used Kivy as GUI framework. I switched the version from 2.0x to 3.00 mainly just because of a name change and to get the main version number even to the main version number of my dashboard.

![Alt text](/screenshots/ARISC_01.png?raw=true "Screenshot 01")

![Alt text](/screenshots/ARISC_02.png?raw=true "Screenshot 02")

![Alt text](/screenshots/ARISC_03.png?raw=true "Screenshot 03")
