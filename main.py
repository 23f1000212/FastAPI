import os
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, Query

load_dotenv()

app = FastAPI()

# Simulate the OS environment variables given in the assignment.
# Remove these two lines if you actually set APP_DEBUG and APP_API_KEY
# in your deployment environment.
os.environ.setdefault("APP_DEBUG", "true")
os.environ.setdefault("APP_API_KEY", "key-q10bkg4x34")

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def to_bool(value):
    return str(value).lower() in ["true", "1", "yes", "on"]


def coerce(key, value):
    if key in ("port", "workers"):
        return int(value)

    if key == "debug":
        return to_bool(value)

    return str(value)


@app.get("/effective-config")
def effective_config(set: list[str] | None = Query(default=None)):
    config = DEFAULTS.copy()

    # YAML layer
    with open("config.development.yaml") as f:
        yaml_config = yaml.safe_load(f)

    for k, v in yaml_config.items():
        config[k] = coerce(k, v)

    # .env layer
    for key, value in os.environ.items():

        if key == "NUM_WORKERS":
            config["workers"] = int(value)

    # APP_* layer
    for key, value in os.environ.items():

        if key.startswith("APP_"):
            actual = key[4:].lower()

            config[actual] = coerce(actual, value)

    # CLI overrides
    if set:

        for item in set:

            if "=" not in item:
                continue

            k, v = item.split("=", 1)

            config[k] = coerce(k, v)

    # Mask secret
    config["api_key"] = "****"

    return config
