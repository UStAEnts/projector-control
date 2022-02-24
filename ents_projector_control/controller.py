import sys
import json
import os.path
from typing import List, Dict

# Constants retrieved from
# https://github.com/signageos/nec-pd-sdk/blob/17aecc4b3a98774e395cfe52ae94be6a3fbf5de6/src/constants.ts
from ents_projector_control.projector import Projector, PowerState
from ents_projector_control.utils import is_pathname_valid

ON = 1
STANDBY = 2
SUSPEND = 3
OFF = 4


def load_configuration():
    locations = [
        # Config file in /etc/ents
        '/etc/ents/projectors.json',
        # Config file in the home directory
        os.path.join(os.path.expanduser("~"), '.ents-projector-control.config.json'),
        # Config file in the same folder
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json'),
    ]

    # Try to load each location but immediately fail if the path doesn't exist, there's no point trying to read from it
    for location in locations:
        if not is_pathname_valid(location):
            continue
        if not os.path.exists(location):
            continue
        with open(location, 'r', encoding='utf8') as f:
            return json.loads(f.read())

    # Loading immediately returns if it parses so if execution ends up down here the config files didn't exist
    raise FileNotFoundError("Could not find a valid configuration file at any of the available paths. "
                            "Searched: {}".format(", ".join(locations)))


def help():
    name = os.path.basename(__file__)
    print("{} [projector name] [action] [other properties]".format(name))
    print("")
    print("  Actions: ")
    print("     power  - {} [projector name] power [state]".format(name))
    print("         on  : Switches the selected projector on")
    print("         off  : Switches the selected projector off")


def power(projector: str, args: List[str]):
    if len(args) != 1:
        print("Error: state is not provided")
        help()
        return

    state = args[0].lower()
    if state != 'on' and state != 'off':
        print("Error: unknown state {}".format(state))
        help()
        return

    # Make sure the projector exists in the config - these values are case sensitive
    config = load_configuration()  # type: Dict
    if projector not in config['projector']:
        projectors = map(lambda x: "'{}'".format(x), config['projector'].keys())
        print("Error: unknown projector: '{}' is not in the config, "
              "must be one of {}".format(projector, ', '.join(projectors)))
        help()
        return

    # Try and connect - this is where things will go wrong
    ip = config['projector'][projector]
    try:
        client = Projector(ip)
        client.connect()
        # client = NECPD.from_ip_address(ip)
    except PDError as e:
        print("Failed to connect to the projector due to an error: {}".format(e))
        return

    # Try getting the current power state as a way to avoid sending the same state is already is (on when it's already
    # on for example) and also as a means to test the connection. Then issue the command if the states don't match
    power_state = client.get_power_state()

    if state == 'on':
        if power_state == PowerState.ON:
            print("Warn: projector is already on, doing nothing")
            return

        client.power_on()
    elif state == 'off':
        if power_state == PowerState.STANDBY:
            print("Warn: projector is already off, doing nothing")
            return

        client.power_off()

    client.close()


def main():
    if len(sys.argv) < 3:
        print("Error: not enough arguments")
        help()
        return

    # Pull out the projector name and action as they will always be required regardless of command
    [_, projector, action, *_] = sys.argv
    # type: str
    action = action.lower()

    # Only power is implemented for the time being. When passing to a function it is best to trim the arguments so
    # each function doesn't have to go wading through the contents
    if action == 'power':
        power(projector, sys.argv[3:])
    else:
        print("Error: unknown action {}".format(action))
        help()


if __name__ == '__main__':
    main()
