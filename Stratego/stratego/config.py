import yaml

with open("config.yml", "r") as yml_file:
    config = yaml.load(yml_file, Loader=yaml.Loader)

# BOARD CHECKS

# Make sure we have a square
assert (config['board']['rows'] == config['board']['columns'])

# Don't allow board size and row/column count that don't evenly divide
assert (config['board']['size'] % config['board']['rows'] == 0)


# WINDOW CHECKS

# Our screen width should be greater than our screen height
assert (config['window']['width'] >= config['window']['height'])
