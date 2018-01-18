#!bin/python

from app import app
import os
from app.state import State
from app.config import Config
from app.cluster import HealthCheck


if not os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    config = Config()
    state = State()
    h_check = HealthCheck(state,config)
    h_check.start()

app.run(debug = True,host='0.0.0.0')

