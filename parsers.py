from ivl_structures import IvlModule, IvlPort
from ivl_elabs import IvlElabNetPartSelect, IvlElabPosedge, IvlElabLogic
from ivl_enums import IvlElabType, IvlPortType, IvlDataDirection
from utils import leading_spaces, is_local_finder, group_lines

import re

ELAB_TYPE_LOOKUP = {
    'NetPartSelect': IvlElabType.net_part_select,
    'posedge': IvlElabType.posedge,
    'logic': IvlElabType.logic
}


def parse_netlist_to_sections(raw_netlist):
    section_regex = '[A-Z][A-Z ]*:.*'
    section_finder = re.compile(section_regex)
    sections = {}
    title = None
    section = []
    for line in raw_netlist.split('\n'):
        if section_finder.match(line):
            if not section:
                section = None
            if title:
                sections[title] = section
            section = []
            title, data = line.split(':')
            if data:
                section = data.strip()
        else:
            section.append(line)
    if title:
        sections[title] = section
    return sections


def parse_module_lines(lines, net_manager):
    module_meta = lines[0]
    module_data = lines[1:]
    name, supertype, module_type_raw, inst_type = module_meta.split(' ')
    module_type = module_type_raw.lstrip('<').rstrip('>')
    ports = parse_module_data(module_data, net_manager)
    module = IvlModule(name, module_type, ports)
    for port in ports:
        port.parent_module = module
    return module


def parse_module_data(lines, net_manager):
    ports = []
    port = None
    skip = True
    for line in lines:
        if leading_spaces(line) == 4:
            if not skip:
                ports.append(port)
                port = None
            else:
                skip = False
            line = line.lstrip(' ')
            if line.startswith('reg') or line.startswith('wire'):
                is_local = is_local_finder.search(line)
                if line.startswith('reg'):
                    xtype = IvlPortType.reg
                else:
                    xtype = IvlPortType.wire
                name = line.split(': ')[1].split('[')[0]
                direction_raw = (line
                                 .split('logic')[1]
                                 .split('(eref')[0]
                                 .strip(' '))
                try:
                    direction = IvlDataDirection[direction_raw]
                except KeyError:
                    direction = None
                width = int(line
                            .split('vector_width=')[1]
                            .split(' pin_count=')[0])
                port = IvlPort(name, xtype, width=width, direction=direction,
                               is_local=is_local)
            elif line.startswith('event'):
                xtype = IvlPortType.event
                name = line.split('event ')[1].split(';')[0]
                snippet = line.split('// ')[1]
                port = IvlPort(name, xtype, code_snippet=snippet)
            else:
                skip = True
        elif leading_spaces(line) == 8:
            if port:
                net_id, net_name = line.split(': ')[1].split(' ')
                net_manager.add_port_to_net(net_id, net_name, port)
    if port:
        ports.append(port)
    return ports


def parse_elab_bundle_lines(lines, net_manager):
    xtype_raw = lines[0].split(' -> ')[0].split('(')[0].split(':')[0]
    xtype = ELAB_TYPE_LOOKUP[xtype_raw]
    info_split = lines[0].split(' ')
    if xtype is IvlElabType.net_part_select:
        io_size_flag = lines[0].split('(')[1].split(')')[0]
        offset = int(info_split[3][4:])
        width = int(info_split[4][4:])
        if io_size_flag == 'PV':
            large_net = IvlDataDirection.output
        elif io_size_flag == 'VP':
            large_net = IvlDataDirection.input
        else:
            raise ValueError('Invalid IO size flag: %s' % io_size_flag)
    elif xtype is IvlElabType.logic:
        logic_type = info_split[1]
    input_nets = []
    output_nets = []
    for line in lines[1:]:
        line_split = line.split(' ')
        data_dir = line_split[6]
        net_id = line_split[9]
        net_name = line_split[10]
        net = net_manager.get_or_make_net(net_id, net_name)
        if data_dir == 'I':
            input_nets.append(net)
        elif data_dir == 'O':
            output_nets.append(net)
        else:
            raise ValueError('Invalid net data direction: %s' % data_dir)
    if xtype is IvlElabType.net_part_select:
        elab = IvlElabNetPartSelect(input_nets[0], output_nets[0], large_net,
                                    offset, width)
    elif xtype is IvlElabType.posedge:
        elab = IvlElabPosedge(input_nets[0])
    elif xtype is IvlElabType.logic:
        elab = IvlElabLogic(logic_type, input_nets, output_nets[0])
    else:
        raise ValueError('Invalid elab xtype: %s' % xtype)
    return elab


def parse_modules_and_elabs(raw_netlist, net_manager):
    sections = parse_netlist_to_sections(raw_netlist)
    modules_lines = group_lines(sections['SCOPES'])
    elab_bundles_lines = group_lines(sections['ELABORATED NODES'])

    modules = [parse_module_lines(lines, net_manager)
               for lines in modules_lines]
    elabs = [parse_elab_bundle_lines(lines, net_manager)
             for lines in elab_bundles_lines]
    return modules, elabs
