#!/usr/bin/python3
# -*- coding: utf-8 -*-
from klausuromat import generator

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
