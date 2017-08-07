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
echo "Building Csv File Import Dialog resource ..."
pyuic5 --from-imports csv_file_import_dialog.ui -o ${targetdir}/csv_file_import_dialog_rc.py
echo "Building Settings Dialog resource ..."
pyuic5 --from-imports settings_dialog.ui -o ${targetdir}/settings_dialog_rc.py
echo "Building Create Visit Dialog resource ..."
pyuic5 --from-imports create_visit_dialog.ui -o ${targetdir}/create_visit_dialog_rc.py
echo "Building Customer Http Dialog resource ..."
pyuic5 --from-imports get_customers_http_dialog.ui -o ${targetdir}/get_customers_http_dialog_rc.py
echo "Building Product Http Dialog resource ..."
pyuic5 --from-imports get_products_http_dialog.ui -o ${targetdir}/get_products_http_dialog_rc.py
echo "Building Create Report Dialog resource ..."
pyuic5 --from-imports create_report_dialog.ui -o ${targetdir}/create_report_dialog_rc.py
echo "   Done!"
cd ${builddir}
