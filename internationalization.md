# Internationalization

1. Generate `.po` files:
```
cd metashare/
python ../manage.py makemessages --all
```

2. Archive `.po` files by language while keeping their paths:
```
cd metashare/
mkdir po_files/en_IE
mkdir po_files/es_ES
mkdir po_files/ga_IE
mkdir po_files/pt_PT
mkdir po_files/fr_FR
find . -path "*en_IE*" -name "django*.po" | xargs cp --parents -t po_files/en_IE
find . -path "*es_ES*" -name "django*.po" | xargs cp --parents -t po_files/es_ES
find . -path "*ga_IE*" -name "django*.po" | xargs cp --parents -t po_files/ga_IE
find . -path "*pt_PT*" -name "django*.po" | xargs cp --parents -t po_files/pt_PT
find . -path "*fr_FR*" -name "django*.po" | xargs cp --parents -t po_files/fr_FR
zip -r po_files-en_IE-date.zip po_files/en_IE
zip -r po_files-es_ES-date.zip po_files/es_ES
zip -r po_files-ga_IE-date.zip po_files/ga_IE
zip -r po_files-pt_PT-date.zip po_files/pt_PT
zip -r po_files-fr_FR-date.zip po_files/fr_FR
```

3. Translate `.po` files (re-ziping the files by observing the same directory structure).

4. Copy translated `.po` files:
```
cd metashare/
unzip po_files-en_IE-date.zip
unzip po_files-es_ES-date.zip
unzip po_files-ga_IE-date.zip
unzip po_files-pt_PT-date.zip
unzip po_files-fr_FR-date.zip
# The last dot is needed (to update current directory contents with contents from the po_files directory extracted from the .zip file received from the translators)
rsync -rtvc po_files/en_IE/ .
rsync -rtvc po_files/es_ES/ .
rsync -rtvc po_files/ga_IE/ .
rsync -rtvc po_files/pt_PT/ .
rsync -rtvc po_files/fr_FR/ .
```

5. With theses new `.po` files, generate the `.mo` files:
```
cd metashare/
python ../manage.py compilemessages
```
