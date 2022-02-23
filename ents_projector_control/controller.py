import sys
import json
import os.path
from typing import List, Dict

from nec_pd_sdk.nec_pd_sdk import NECPD
from nec_pd_sdk.protocol import PDError

ON = 1
STANDBY = 2
SUSPEND = 3
OFF = 4


def load_configuration():
    locations = [
        # Config file in the same folder
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json'),
        # Config file in the home directory
        os.path.join(os.path.expanduser("~"), '.ents-projector-control.config.json'),
        # Config file in /etc/ents
        '/etc/ents/projectors.json',
    ]

    for location in locations:
        if not os.path.exists(location):
            break
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json'), 'r',
                  encoding='utf8') as f:
            return json.loads(f.read())

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

    config = load_configuration()  # type: Dict
    if projector not in config['projector']:
        projectors = map(lambda x: "'{}'".format(x), config['projector'].keys())
        print("Error: unknown projector: '{}' is not in the config, "
              "must be one of {}".format(projector, ', '.join(projectors)))
        help()
        return

    ip = config['projector'][projector]
    try:
        client = NECPD.from_ip_address(ip)
    except PDError as e:
        print("Failed to connect to the projector due to an error: {}".format(e))
        return

    power_state = client.command_power_status_read()

    if state == 'on':
        if power_state == ON:
            print("Warn: projector is already on, doing nothing")
            return

        client.command_power_status_set(ON)
    elif state == 'off':
        if power_state == OFF:
            print("Warn: projector is already off, doing nothing")
            return

        client.command_power_status_set(OFF)


def main():
    if len(sys.argv) < 3:
        print("Error: not enough arguments")
        help()
        return

    [_, projector, action, *rest] = sys.argv
    # type: str
    action = action.lower()

    if action == 'power':
        power(projector, sys.argv[3:])
    else:
        print("Error: unknown action {}".format(action))
        help()


if __name__ == '__main__':
    main()
