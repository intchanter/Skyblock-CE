Skyblock-CE
###########

A community-maintained version of the famous Skyblock map by Noobcrew

Prerequisites
=============

* A computer with a Unix-like operating system (including Mac and Linux)
* Python 2.7 (available by default on many systems)
* pip (sudo easy_install pip)
* virtualenv (sudo pip install virtualenv)
* virtualenvwrapper (sudo pip install virtualenvwrapper, then additional steps
  from http://virtualenvwrapper.readthedocs.org/en/latest/install.html)
* -dev or -devel packages as required by the packages in requirements.txt - please submit an issue on Github if you have some of these missing so we can update this as necessary

Getting Started
===============

1. Ensure you have met the prerequisites above.

2. Create and switch to your virtualenv:

 $ mkvirtualenv --python=<path to python-2.7> skyblock-ce

3. Get the dependencies for pymclevel:

 $ pip install -r requirements.txt

4. Get pymclevel:

 $ pip install -r requirements2.txt

Note: pymclevel's installer doesn't currently install its required .yaml
files. You can download them from the repository mentioned in
requirements2.txt or clone the repository and copy them locally to
~/.virtualenvs/skyblock-ce/lib/python-?.?/site-packages/pymclevel/ until this
pull request is merged: https://github.com/mcedit/pymclevel/pull/180

5a. Run the build script

 $ ./build.py

5b. (Optional, only for distribution) Run the zip script

 $ ./zip.sh
