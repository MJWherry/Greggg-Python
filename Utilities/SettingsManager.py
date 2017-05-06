import xml.etree.ElementTree as ET

from termcolor import colored


class SettingsManager:
    file_path = 'config.xml'
    settings_name = ''
    settings = []

    def __init__(self, settings_name='general', file_path='config.xml'):
        self.settings_name = settings_name
        self.file_path = file_path
        self.load_settings()

    def load_settings(self):
        print colored(' Loading settings type: {} | filepath: {}'.format(self.settings_name, self.file_path), 'yellow')
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            try:
                device = root.find(self.settings_name)
                for child in device.iter('setting'):
                    self.settings.append([child.attrib['name'], child.attrib['value'], child.attrib['default_value']])
            except AttributeError:
                root.append(self.settings_name)
                print ' No setting section named \'{}\', adding the node and continuing.'.format(self.settings_name)
            print colored(' {} settings loaded.'.format(len(self.settings)), 'green')
        except IOError:
            print colored(' Invalid file name/path: {}'.format(self.file_path), 'red')

    def save_settings(self):
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            device = root.find(self.settings_name)
            if device is None:
                print ' MAKING NEW ELEMENT'
                new_element = ET.Element(self.settings_name)
                new_element_settings_tag = ET.Element('settings')
                new_element.append(new_element_settings_tag)
                root.append(new_element)
                device = new_element
            for child in device.iter('setting'):
                child.attrib['value'] = self.get_setting_value(child.attrib['name'])
            tree.write(self.file_path)
        except IOError:
            print colored(' Invalid file name/path: {}'.format(self.file_path), 'red')

    def add_setting(self, setting, value, default):
        self.settings.append((setting, value, default))

    def remove_setting(self, setting_param):
        for setting in self.settings:
            if setting[0] == setting_param:
                self.settings.remove(setting)

    def get_setting_value(self, setting_param):
        for setting in self.settings:
            if setting[0] == setting_param:
                return setting[1]

    def set_setting_value(self, setting_param, value):
        for setting in self.settings:
            if setting[0] == setting_param:
                setting[1] = str(value)

    def set_default_settings(self):
        for setting in self.settings:
            setting[1] = setting[2]

    def set_default_setting(self, name):
        for setting in self.settings:
            if setting[0] == name:
                setting[1] = setting[2]

    def print_settings(self):
        print '', self.settings_name
        for setting in self.settings:
            print ' {} : {}'.format(setting[0], setting[1])

    def get_settings_string(self):
        data = '{' + self.settings_name + '('
        for setting in self.settings:
            data = data + '{}[{}],'.format(setting[0], setting[1])
        data += ')}'
        return data
