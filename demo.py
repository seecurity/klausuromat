#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Externals
import sys
import io
import json

# Internals
import generator


# Get settings
with io.open('settings.json', mode='r', encoding='utf-8') as fd:
    settings = json.load(fd)

# Remote debugging
if settings['REMOTE_DEBUG']:
    sys.path.append('/home/vbox/pycharm/pycharm-debug-py3k.egg')
    import pydevd

    pydevd.settrace('192.168.56.1', port=22222, stdoutToServer=True, stderrToServer=True)

# Create random code generator
gen = generator.RandomCodeGenerator()

# Levels
gen.operator_level = '3'  # max: 3
gen.pointer_level = '2'  # max: 2
gen.function_level = '2'  # max: 2

# Booleans
gen.void = False
gen.float_ = True
gen.conditionals = True

# Print generated code
print(gen.code())