#!/usr/bin/env python

import pathlib
import shutil
import sys

for f in pathlib.Path(sys.argv[1]).glob("**/*.coverage*"):
    print("Collecting", f)
    shutil.move(str(f), sys.argv[2])
