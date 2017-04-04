import xml.etree.ElementTree as ET

tree = ET.parse('config.xml')
root = tree.getroot()

device = root.find('gps')
# Settings
print 'SETTINGS'
for child in device.iter('setting'):
    print child.attrib['name'], ':', child.attrib['value']

# Hardware commands
print '\nHARDWARE COMMANDS'
for child in device.iter('hardware_commands'):
    for command in child.iter('command'):
        print command.attrib['name'], command.attrib['parameter_count']
        for parameter in command.iter('parameter'):
            print '<', parameter.attrib['type'], '>', '(', parameter.attrib['range'], ')', parameter.attrib['description']

# Terminal commands
print '\nTERMINAL COMMANDS'
for child in device.iter('terminal_commands'):
    for command in child.iter('command'):
        print command.attrib['name'], ': ', command.attrib['description']