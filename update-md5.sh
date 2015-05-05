#!/bin/sh
cd source
md5sum codedict database.py __init__.py processor.py > checksums.md5
