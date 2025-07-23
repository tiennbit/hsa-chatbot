#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin Blueprint
"""

from flask import Blueprint

admin_bp = Blueprint('admin', __name__, template_folder='templates')

from . import routes

