from ivl_enums import IvlElabType, IvlDataDirection


class IvlElab:
    def __init__(self, xtype):
        self.xtype = xtype

    def __repr__(self):
        return '<IvlElab: %s>' % self.xtype.name


class IvlElabPosedge(IvlElab):
    def __init__(self, net_in):
        IvlElab.__init__(self, IvlElabType.posedge)
        self.net_in = net_in

    def __repr__(self):
        pre = super().__repr__()
        head = pre[:-1]
        output = head
        output += ': event on %s' % self.net_in.name
        output += '>'
        return output


class IvlElabNetPartSelect(IvlElab):
    def __init__(self, net_in, net_out, large_net, bit_pos, pin_count):
        IvlElab.__init__(self, IvlElabType.net_part_select)
        self.net_in = net_in
        self.net_out = net_out
        self.large_net = large_net
        self.bit_pos = bit_pos
        self.pin_count = pin_count

    def __repr__(self):
        last_pin = self.bit_pos + self.pin_count - 1
        bit_pos_count = '[%s:%s]' % (self.bit_pos, last_pin)
        pre = super().__repr__()
        head = pre[:-1]
        output = head
        output += ': %s' % self.net_in.name
        if self.large_net is IvlDataDirection.input:
            output += bit_pos_count
        output += ' -> %s' % self.net_out.name
        if self.large_net is IvlDataDirection.output:
            output += bit_pos_count
        output += '>'
        return output


class IvlElabLogic(IvlElab):
    def __init__(self, logic_type, nets_in, net_out):
        IvlElab.__init__(self, IvlElabType.logic)
        self.logic_type = logic_type
        self.nets_in = nets_in
        self.net_out = net_out

    def __repr__(self):
        pre = super().__repr__()
        head = pre[:-1]
        output = head + ': '
        output += '%s: ' % self.logic_type
        output += '%s -> ' % ', '.join([n.name for n in self.nets_in])
        output += '%s>' % self.net_out.name
        return output
