# GNOME Feeds
A Soon to be RSS Reader for GNOME under the GPLv3 License.
## Building on Ubuntu/Debian ##

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
## Building on Arch/Manjaro ##
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
