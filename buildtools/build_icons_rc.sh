#!/bin/bash
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

# init
builddir=${PWD}
targetdir="../../resources"

# building icons
cd ${builddir}/icons
python ${builddir}/qrc-icons.py
echo "Building system icon resource ..."
pyrcc5 system.qrc -o ${targetdir}/system_rc.py

# building graphics
cd ${builddir}/graphics
python ${builddir}/qrc-graphics.py
echo "Building splash resource ..."
pyrcc5 splash.qrc -o ${targetdir}/splash_rc.py

# done
echo "   Done!"
cd ${builddir}

