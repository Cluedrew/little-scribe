#/usr/bin/env python3
"""Scribbler, the default Little Scribe compiler."""

# I was going to start work on this but then I realized I actually
# hadn't though about the interface.

import argparse
import sys


argparser = argparse.ArgumentParser(
    description='Scribbler, the default Little Scribe compiler.')

if 1 == len(sys.argv):
    pass
