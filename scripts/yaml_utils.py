import yaml

YAML_WIDTH = 100
YAML_INDENT = 2

class LiteralString(str):
    pass

def literal_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='>')
yaml.add_representer(LiteralString, literal_presenter)

def comment_line(line):
    return "# {} # ".format(line.ljust(YAML_WIDTH + YAML_INDENT))
