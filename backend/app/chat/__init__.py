#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chat Blueprint
"""

from flask import Blueprint

chat_bp = Blueprint('chat', __name__, template_folder='templates')

from . import routes 