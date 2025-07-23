#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Blueprint
"""

from flask import Blueprint

api_bp = Blueprint('api', __name__)

from . import routes 