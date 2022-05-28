#!/usr/bin/env python

import json
import subprocess
import sys

cmd = ['pip', 'list', '--format', 'json']
proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
packages = {
    package['name']: package
    for package in json.loads(proc.stdout)
}
for expected in ('marbles.core', 'marbles.mixins'):
    try:
        packages[expected]['editable_project_location']
    except KeyError:
        break
else:
    sys.exit(0)

cmd = ['pip', 'install', '-e', 'marbles/core', '-e', 'marbles/mixins']
proc = subprocess.run(cmd, check=True)
sys.exit(proc.returncode)
