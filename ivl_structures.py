class IvlModule:
    def __init__(self, name, xtype, ports=None):
        self.name = name
        self.xtype = xtype
        self.ports = ports or []

    def __repr__(self):
        return '<IvlModule: %s "%s" (%s ports)>' % (self.xtype, self.name,
                                                    len(self.ports))


class IvlPort:
    def __init__(self, name, xtype, width=None, code_snippet=None, net=None,
                 is_local=False, direction=None, parent_module=None):
        self.name = name
        self.xtype = xtype
        self.width = width
        self.code_snippet = code_snippet
        self.net = net or set()
        self.is_local = is_local
        self.direction = direction
        self.parent_module = parent_module

    def set_net(self, net):
        self.net = net

    def remove_net(self, net):
        self.nets.remove(net)

    def __repr__(self):
        output = '<IvlPort: '

        if self.direction:
            output += '%s ' % self.direction.name

        if self.is_local:
            output += 'local '

        output += '%s ' % self.xtype.name

        output += '"%s" ' % self.name

        if self.parent_module:
            output += 'on %s ' % self.parent_module.name

        if self.code_snippet:
            output += '@ %s ' % self.code_snippet

        output = output[:-1]
        output += '>'
        return output


class IvlNet:
    def __init__(self, xid, name, members=None):
        self.xid = xid
        self.name = name
        self.members = members or set()

    def add_member(self, member):
        self.members.add(member)

    def remove_member(self, member):
        self.members.remove(member)

    def has_member(self, member):
        return member in self.members

    def __repr__(self):
        return '<IvlNet: "%s" (%s members)>' % (self.name, len(self.members))
