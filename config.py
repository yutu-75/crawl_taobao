from configparser import ConfigParser
from pathlib import Path

config_root_path = Path(__file__)

config_path = {
    'global': config_root_path.parent.joinpath('config.ini'),
    # 'eth': config_root_path.joinpath('eth', 'config.ini'),
}

config_ini = {

}


def read_ini(path):
    """
    configparser 读取配置文件
    :return: [dict]
    """
    print(config_root_path.parent.joinpath('config.ini'))
    config_parser = ConfigParser()

    config_parser.read(config_path.get(path), encoding='utf-8')
    return config_parser


def get_config(name):
    global config_ini
    if name not in config_ini:
        config_ini[name] = read_ini(config_path['name'])
    return config_ini[name]


config = read_ini('global')

if __name__ == '__main__':

    print(config.get("database", "host"))
