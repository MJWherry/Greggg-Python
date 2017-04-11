import xml.etree.ElementTree as ET

tree = ET.parse('config.xml')
root = tree.getroot()

device = root.find('motor')
# Settings
print 'SETTINGS'
for child in device.iter('setting'):
    print child.attrib['name'], ':', child.attrib['value']

# Hardware commands
print '\nHARDWARE COMMANDS'
valid_motor_commands = []
for child in device.iter('hardware_commands'):
    for command in child.iter('command'):
        valid_command = (command.attrib['name'], command.attrib['parameter_count'],[])
        for parameter in command.iter('parameter'):
            valid_command[2].append((parameter.attrib['type'], parameter.attrib['range'], parameter.attrib['description']))
        valid_motor_commands.append(valid_command)
print valid_motor_commands
# Terminal commands
print '\nTERMINAL COMMANDS'
for child in device.iter('terminal_commands'):
    for command in child.iter('command'):
        print command.attrib['name'], ': ', command.attrib['description']