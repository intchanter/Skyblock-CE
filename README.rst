Skyblock-CE
###########

A community-maintained version of the famous Skyblock map by Noobcrew

Prerequisites
=============

* A computer with a Unix-like operating system (including Mac and Linux)
* Python 2.7 (available by default on many systems)
* pip (sudo easy_install pip)
* virtualenv (sudo pip install virtualenv)
* virtualenvwrapper (sudo pip install virtualenvwrapper)
* -dev or -devel packages as required by the packages in requirements.txt - please submit an issue on Github if you have some of these missing so we can update this as necessary

Getting Started
===============

1. Create and switch to your virtualenv:

 $ mkvirtualenv --python=<path to python-2.7> skyblock-ce

2. Get the dependencies for pymclevel:

 $ pip install -r requirements.txt

3. Get pymclevel:

 $ pip install -r requirements2.txt

4a. Run the build script

 $ ./build.py

4b. (Optional, only for distribution) Run the zip script

 $ ./zip.sh

5. Realize that installing pymclevel didn't grab its required minecraft.yaml and manually download it into the library directory in the virtualenv.  Duplicate the effort for classic.yaml, indev.yaml, pocket.yaml, ...
