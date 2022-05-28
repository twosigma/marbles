#!/usr/bin/env python

from shutil import rmtree
import sys

for d in sys.argv[1:]:
    rmtree(d, True)
