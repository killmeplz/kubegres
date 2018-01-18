#!bin/python

import os

from app import app
from app.cluster import HealthCheck
from app.config import Config
from app.state import State

if not os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    config = Config()
    state = State()
    h_check = HealthCheck(state, config)
    h_check.start()

app.run(debug=True, host='0.0.0.0')
