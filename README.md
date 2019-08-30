# <a href="https://gabmus.gitlab.io/gnome-feeds"><img height="32" src="data/icons/org.gabmus.gfeeds.svg" /> Feeds</a>

An RSS/Atom feed reader for GNOME.

![screenshot](website/screenshots/mainwindow.png)

## Notes on the distribution of this app

I decided to target flatpak mainly. It's just another package manager at the end of the day, but
it's supported by many Linux distributions. It bundles all of the dependencies you need in one
package.

This helps a lot in supporting many different distros because I know which version of which
dependency you have installed, so I don't have to mess with issues caused by version mismatches.
If you want to report an issue, feel free to. But please at least first see if this issue happens
with the flatpak version as well.

As for development it's a similar story. I do most of my testing directly inside a flatpak sandbox
and you should do the same. It's easy to set up, just open up this repo in GNOME Builder and press
the run button. It will handle the rest.

## Installing from Flathub

You can install Feeds via [Flatpak](https://flathub.org/apps/details/org.gabmus.gnome-feeds).

## Installing from AUR

Feeds is available as an AUR package: [`gnome-feeds-git`](https://aur.archlinux.org/packages/gnome-feeds-git/).

## Installing from Fedora

Feeds is available in [Fedora repos](https://apps.fedoraproject.org/packages/gnome-feeds): `sudo dnf install gnome-feeds`

# Building on different distributions

**Note**: these are illustrative instructions. If you're a developer or a package maintainer, they
can be useful to you. If not, just install the flatpak.

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
