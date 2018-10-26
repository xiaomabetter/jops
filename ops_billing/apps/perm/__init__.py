from flask import Blueprint

perm = Blueprint('perm', __name__)

from .view import *