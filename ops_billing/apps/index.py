from flask import render_template
from apps import app
from apps.auth import login_required

@app.route('/')
@login_required
def index():
    return render_template('base/index.html')