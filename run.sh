#!/bin/bash

gunicorn --bind 0.0.0.0:8080 --daemon --pid app.pid --workers 4 --error-logfile logs/error.log --access-logfile logs/access.log run:app

