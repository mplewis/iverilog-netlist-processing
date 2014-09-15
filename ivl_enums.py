from enum import Enum


class IvlPortType(Enum):
    reg = 1
    wire = 2
    event = 3


class IvlDataDirection(Enum):
    input = 1
    output = 2


class IvlElabType(Enum):
    net_part_select = 1
    logic = 2
    posedge = 3
