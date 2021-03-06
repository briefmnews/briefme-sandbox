import os
import json


pth = os.path.dirname(__file__)


schemas = {}
for filename in os.listdir(pth):
    if filename.endswith(".json"):
        key = filename[:-5]
        with open(os.path.join(pth, filename)) as json_file:
            schemas[key] = json.load(json_file)

html_fields = {
    "rewind": ["text"],
    "basic": ["text"],
    "image": ["text"],
    "questions": ["answer"],
    "quote": ["text", "quote"],
    "start": ["intro", "p", "text"],
}
