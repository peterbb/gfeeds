## Installing from Flathub

You can install Feeds via [Flatpak](https://flathub.org/apps/details/org.gabmus.gnome-feeds).

## Installing from AUR

Feeds is available as an AUR package: [`gnome-feeds-git`](https://aur.archlinux.org/packages/gnome-feeds-git/).

## Building on Ubuntu/Debian

```bash
sudo apt-get install python-html5lib webkit2gtk python-lxml python-requests
sudo pip install listparser 

git clone https://gitlab.gnome.org/GabMus/gnome-feeds
cd gnome-feeds
mkdir build
cd build
meson ..
ninja
ninja install
```

## Building on Arch/Manjaro

```bash
sudo pacman -S python-html5lib webkit2gtk python-lxml python-requests python-pip python-gobject python-feedparser
sudo pip install listparser 

git clone https://gitlab.gnome.org/GabMus/gnome-feeds
cd gnome-feeds
mkdir build
cd build
meson ..
ninja
ninja install
```
