import os
import json
dirFile = os.path.normpath(os.path.join(os.path.realpath(__file__), os.pardir))
with open('{}/config.json'.format(dirFile)) as f:
    DEFAULT = json.load(f)
NODATAVAL = -9999
