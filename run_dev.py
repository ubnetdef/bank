#!/usr/bin/env python
from app import app, scheduler

scheduler.start()
app.run()