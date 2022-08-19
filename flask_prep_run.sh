#!/bin/bash
source virt/bin/activate 
export FLASK_APP=hello.py 
export FLASK_ENV=development 
flask run