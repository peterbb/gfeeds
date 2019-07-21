#!/bin/bash

rm *.pot
version=$(fgrep "version: " ../meson.build | grep -v "meson" | grep -o "'.*'" | sed "s/'//g")
find ../hydrapaper -iname "*.py" | xargs xgettext --package-name=HydraPaper --package-version=$version --from-code=UTF-8 --output=hydrapaper-python.pot
find ../data/ui -iname "*.glade" -or -iname "*.xml" | xargs xgettext --package-name=HydraPaper --package-version=$version --from-code=UTF-8 --output=hydrapaper-glade.pot -L Glade
find ../data/ -iname "*.desktop.in" | xargs xgettext --package-name=HydraPaper --package-version=$version --from-code=UTF-8 --output=hydrapaper-desktop.pot -L Desktop
find ../data/ -iname "*.appdata.xml.in" | xargs xgettext --no-wrap --package-name=HydraPaper --package-version=$version --from-code=UTF-8 --output=hydrapaper-appdata.pot
msgcat --use-first hydrapaper-python.pot hydrapaper-glade.pot hydrapaper-desktop.pot hydrapaper-appdata.pot > hydrapaper.pot
sed 's/#: //g;s/:[0-9]*//g;s/\.\.\///g' <(fgrep "#: " hydrapaper.pot) | sort | uniq > POTFILES.in
echo "# Please keep this list alphabetically sorted" > LINGUAS
for l in $(ls *.po); do basename $l .po >> LINGUAS; done
for lang in $(sed "s/^#.*$//g" LINGUAS); do
    mv "${lang}.po" "${lang}.po.old"
    msginit --locale=$lang --input hydrapaper.pot
    mv "${lang}.po" "${lang}.po.new"
    msgmerge -N "${lang}.po.old" "${lang}.po.new" > ${lang}.po
    rm "${lang}.po.old" "${lang}.po.new"
done
rm *.pot

# To create lang file use this command
# msginit --locale=LOCALE --input hydrapaper.pot
# where LOCALE is something like `de`, `it`, `es`...
