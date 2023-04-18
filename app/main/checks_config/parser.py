import configparser

checks_config = configparser.ConfigParser()
checks_config.read('app/main/checks_config/main.ini')

sld_num = dict(checks_config['sld_num_check'])
sld_num = dict([a, list(map(int, x.split(',')))] for a, x in sld_num.items())
