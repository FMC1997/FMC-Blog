#!/bin/bash
source virt/bin/activate 
export FLASK_APP=app.py 
export FLASK_ENV=development 
flask run