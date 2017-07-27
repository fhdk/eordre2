#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

builddir=${PWD}
targetdir="../../resources"
cd ./ui
echo "Building Main Window resource ..."
pyuic5 --from-imports main_window.ui -o ${targetdir}/main_window_rc.py
echo "Building File Import Dialog resource ..."
pyuic5 --from-imports file_import_dialog.ui -o ${targetdir}/file_import_dialog_rc.py
echo "Building Settings Dialog resource ..."
pyuic5 --from-imports settings_dialog.ui -o ${targetdir}/settings_dialog_rc.py
echo "Building Order Dialog resource ..."
pyuic5 --from-imports order_dialog.ui -o ${targetdir}/order_dialog_rc.py
echo "Building Http Customer Import Dialog resource ..."
pyuic5 --from-imports http_cust_import_dialog.ui -o ${targetdir}/http_cust_import_dialog_rc.py
echo "Building Http Product Import Dialog resource ..."
pyuic5 --from-imports http_prod_import_dialog.ui -o ${targetdir}/http_prod_import_dialog_rc.py
echo "Building Create Report Dialog resource ..."
pyuic5 --from-imports create_report_dialog.ui -o ${targetdir}/create_report_dialog_rc.py
echo "   Done!"
cd ${builddir}
