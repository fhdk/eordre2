#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import sys

icons = "/icons/"
icon_res_path = os.getenv("PWD")
icon_dirs = ["system"]

for icon_dir in icon_dirs:
    walk_path = icon_res_path + "/" + icon_dir
    f = []
    for (dirpath, dirnames, filenames) in os.walk(walk_path):
        f.extend(filenames)
        break
    outfile = "{}.qrc".format(icon_dir)
    with open(outfile, "w") as resfile:
        resfile.write("<RCC>\n  <qresource prefix=\"{}\">\n".format(icons))
        for icon_name in f:
            resfile.write("    <file>{}/{}</file>\n".format(icon_dir, icon_name))
        resfile.write("  </qresource>\n</RCC>\n")
