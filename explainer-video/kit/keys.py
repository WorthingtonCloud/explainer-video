"""API keys for the paid scripts: from the environment, else from the nearest .env, looking in the project folder first
and then in each folder above it (so one .env over all your projects works)."""
import os, sys


def key(name):
    if os.environ.get(name): return os.environ[name].strip()
    d = os.getcwd()
    while True:
        f = os.path.join(d, ".env")
        if os.path.exists(f):
            for line in open(f):
                if line.startswith(name + "="): return line.split("=", 1)[1].strip().strip('"').strip("'")
        if os.path.dirname(d) == d: break
        d = os.path.dirname(d)
    sys.exit(f"{name} missing: set it in the environment, or in a .env file in this folder or any folder above it")
