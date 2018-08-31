from flask import Blueprint

task = Blueprint('task', __name__)

from .view import *

from .tasks.ansibe import *
from .tasks.asset import *