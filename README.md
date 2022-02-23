# ents-projector-control

This repo contains the projector controller for the Ents Crew. This script is built and installed to the Raspberry Pi controller in AV Rack. For more information [see the wiki](https://wiki.entscrew.net/).

## Configuration

This program is configured through a JSON configuration file which contains mappings of projectors to their IP addresses used by the NEC SDK. This file can exist in three places:

* `./config.json`
* `~/.ents-projector-control.config.json`
* `/etc/ents/projectors.json`

The preferred location is `/etc/ents/projectors.json` for deployment and `./config.json` for development. The file currently contains one object (`projectors`) that contains projector name to ip address mappings. For example

```json
{
  "projector": {
    "name": "ip address"
  }
}
```

## Executing

Once installed this package makes one command available through the Poetry configuration: `projector-control`. The syntax is displayed in help messages but is copied below for easy reference.

```
projector-control [projector name] [action] [other properties]

  Actions: 
     power  - controller.py [projector name] power [state]
         on   : Switches the selected projector on
         off  : Switches the selected projector off
```