# GNOME Feeds
An RSS/Atom feed Reader for GNOME under the GPLv3 License.

## Installing from Flathub
You can install Feeds via [Flatpak](https://flathub.org/apps/details/org.gabmus.gnome-feeds).

## Building on Ubuntu/Debian

```sh

$ sudo apt-get install python-html5lib webkit2gtk python-lxml python-requests
$ sudo pip install listparser 

$ git clone https://gitlab.gnome.org/GabMus/gnome-feeds
$ cd gnome-feeds
$ mkdir build
$ cd build
$ meson ..
$ ninja
$ ninja install
```
## Building on Arch/Manjaro

```sh

$ sudo pacman -S python-html5lib webkit2gtk python-lxml python-requests python2-pip python-pip
$ sudo pip install listparser 

$ git clone https://gitlab.gnome.org/GabMus/gnome-feeds
$ cd gnome-feeds
$ mkdir build
$ cd build
$ meson ..
$ ninja
$ ninja install
```