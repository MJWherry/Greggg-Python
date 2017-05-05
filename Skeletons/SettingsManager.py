import xml.etree.ElementTree as ET


class SettingsManager:

    file_path = 'config.xml'
    settings = []
    settings_type = ''

    def __init__(self):
        pass

    def load_settings(self, name):
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        device = root.find(name)
        for child in device.iter('setting'):
            self.settings.append([child.attrib['name'], child.attrib['value'], child.attrib['default_value']])
        self.settings_type = name+'_settings'

    def save_settings(self, name):
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        device = root.find(name)
        for child in device.iter('setting'):
            child.attrib['value'] = self.get_setting_value(child.attrib['name'])
        tree.write('config.xml')

    def set_setting_value(self, setting_param, value):
        for setting in self.settings:
            if setting[0] == setting_param:
                setting[1] = str(value)

    def add_setting(self, setting, value, default):
        self.settings.append((setting, value, default))

    def remove_setting(self, setting_param):
        for setting in self.settings:
            if setting[0] == setting_param:
                self.settings.remove(setting)

    def set_default_settings(self):
        for setting in self.settings:
            setting[1] = setting[2]

    def set_default_setting(self, name):
        name = name.lower()
        for setting in self.settings:
            if setting[0] == name:
                setting[1] = setting [2]

    def get_setting_value(self, setting_param):
        for setting in self.settings:
            if setting[0] == setting_param:
                return setting[1]

    def print_settings(self):
        print self.settings_type
        for setting in self.settings:
            print '{} : {}'.format(setting[0], setting[1])

    def get_settings_string(self):
        data = self.settings_type+'('
        for setting in self.settings:
            data = data + '{}[{}],'.format(setting[0], setting[1])
        data += ')'
        return data