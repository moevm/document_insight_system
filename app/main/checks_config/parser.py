import configparser
checks_config = configparser.ConfigParser()
checks_config.read('app/main/checks_config/main.ini')

sld_num_bsc = checks_config.get('sld_num_check', 'bsc').split(',')
sld_num_bsc = list(map(int, sld_num_bsc))

sld_num_msc = checks_config.get('sld_num_check', 'msc').split(',')
sld_num_msc = list(map(int, sld_num_msc))
