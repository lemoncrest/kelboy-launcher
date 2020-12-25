# What is this kelboy-launcher?

This is the official Kelboy Launcher for current boards Kelboy 2.x to be used and supported by the community.

# How it works?

This software is designed to be working without the need to start any graphical environment, so it only requires a bash console with access to the graphics card (pygame requirement).

It is made up of a series of menus through the user can interact and run scripts.

Everything is designed so any user can easily edit menus and include new features to their needes.

Mostly menus are in .json files inside resources path.

There are a lot of examples included in this launcher that provide launch of external tools, scripts and any kind of software.


# Target hardware

All information related to this beautiful boards are in https://shop.lemoncrest.com/index.php

![alt text](https://shop.lemoncrest.com/img/p/4/2/42-large_default.jpg)

It's developed in Python 3 using pygame compatible with Raspbian or Raspberry Pi OS versions.


# Install instructions
```
cd /home/pi/
git clone https://github.com/lemoncrest/kelboy-launcher
```
In bin/ folder there are some interesting scripts for this software. Just use install.sh script to get it working in your kelboy.
```
bin/install.sh
```
Additionally, it's a launcher, so you need to edit .bashrc or some startup file (if you're able to create a service use this option) to get it working. F.I. in .bashrc include:

```
if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    echo "welcome to kelboy throw ssh session"
else
    cd kelboy-launcher
    ./launcher.sh >/dev/null 2>&1 
fi
```
# License
It's licensed with GPLv3, so feel free to learn and use it not only in his target hardware (Kelboy 2 DIY consoles).

We look forward to the community contributing and developing new features

# Credits

There are no secrets, we're opensource.

Developed by Lemoncrest for Kelboy 2.x boards.

More information at:

https://lemoncrest.com/kelboy

If you have some suggestion feel free to contact us in our channels:

(Spanish) -> https://t.me/ProyectoCarcasa

(English) -> https://t.me/LemoncrestEN

Enjoy
