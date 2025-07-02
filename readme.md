# Markdown Bookmark CLI Tool

This is a python Markdown tool Aimed at both a links only approach of replacing a Bookmark manager and a MD content viewer for storing and viewing information inside a terminal

- **md_browser** - Markdown note taking tool
- **link_viewer** - Bookmark link application


## Setup

All of the files exist within the .env file in the repo. The idea is to build up the .md files as vars and the script will enable the functions for you to use.

* link both the `.sh` files to your .bashrc using 
    * `source /path/to/directory/link_viewer.sh`
    * `source /path/to/directory/md_browser.sh`
* Configure the `.env.example` to your relative paths and configure script locations
* Add in MD_FILE_\<name\> for a new link file
* Add in NOTE_FILE_\<name\> for a note file

## Link viewer

Access the link viewer by typing i.e for env entry `MD_FILE_links` 
* linksadd \<url\> \[category\] \[title\] - Add link to markdown file as links list
* links - Browsing information

## MD Browser

Access the MD Browser by typing i.e for env entry `NOTE_FILE_test` 
* testadd - Wizard for add
* test - Browsing information
* testdel - Wizard for delete


## Python Script Usage


**Link viewer**
```
python link_viewer.py --path /path/test.md
python link_viewer.py --path /path/test.md --random
python link_viewer.py --path /path/test.md --add "title" "category"
```

**Link viewer**
```
python md_browser.py "/path/file.md"
python md_browser.py "/path/file.md" add
python md_browser.py "/path/file.md" delete
```
