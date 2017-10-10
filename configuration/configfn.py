#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <echo "ZmhAdWV4LmRrCg==" | base64 -d>
# Copyright: Frede Hundewadt <echo "ZmhAdWV4LmRrCg==" | base64 -d>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Configuration functions"""

from util import filefn

from . import config


def check_config_folder():
    """Checks if the APP_DATA folder exist and creates if not"""
    if not filefn.check_file(config.APP_DATA, folder=True):
        filefn.create_dir(config.APP_DATA)
