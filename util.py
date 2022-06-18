"""Functions for packing struct data"""

import struct

#Support Functions
def write_int(value):
    return struct.pack("<i",value)

def write_float(value):
    return struct.pack("<f",value)

def write_float_couple(value1, value2):
    return struct.pack("<ff", value1, value2)

def write_float_triplet(value1, value2, value3):
    return struct.pack("<fff", value1, value2, value3)

def write_float_quad(value1, value2, value3, value4):
    return struct.pack("<ffff", value1, value2, value3, value4)
    
def write_string(value):
    binary_format = "<%ds"%(len(value)+1)
    return struct.pack(binary_format, str.encode(value))

def write_chunk(name, value):
    dummy = bytearray()
    return dummy + name + write_int(len(value)) + value

