# -*- coding: utf-8 -*-
from apps.initialized import app

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5050)