## Installing from Flathub

You can install Feeds via [Flatpak](https://flathub.org/apps/details/org.gabmus.gfeeds).

## Installing from AUR

Feeds is available as an AUR package: [`gfeeds-git`](https://aur.archlinux.org/packages/gfeeds-git/).

## Building on Ubuntu/Debian

```bash
sudo apt-get install python-html5lib webkit2gtk python-lxml python-requests python-pygments
sudo pip install listparser

git clone https://gitlab.gnome.org/World/gfeeds
cd gfeeds
mkdir build
cd build
meson ..
meson configure -Dprefix=$PWD/testdir # use this line if you want to avoid installing system wide
ninja
ninja install
```

## Building on Arch/Manjaro

```bash
sudo pacman -S python-html5lib webkit2gtk python-lxml python-requests python-pip python-gobject python-feedparser python-pygments
yay -S python-listparser

git clone https://gitlab.gnome.org/GabMus/gfeeds
cd gfeeds
mkdir build
cd build
meson ..
meson configure -Dprefix=$PWD/testdir # use this line if you want to avoid installing system wide
ninja
ninja install
```

## Hacking

You might want to check your code with pyflakes before you commit.

- Ubuntu/Debian: `sudo apt install pyflakes`
- Arch/Manjaro: `sudo pacman -S python-pyflakes`

```bash
pyflakes gfeeds
```
