![GitHub](https://img.shields.io/github/license/alemuro/ha-nissan-connect?style=flat-square)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/alemuro/ha-nissan-connect?style=flat-square)
![GitHub Release Date](https://img.shields.io/github/release-date/alemuro/ha-nissan-connect?style=flat-square)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=alemuro&repository=ha-nissan-connect&category=integration)

# Nissan Connect integration

This integration integrates Nissan vehicles to Home Assistant using Nissan Connect
services.

This project is based on the following projects:

- https://github.com/sebjsmith/kamereon
- https://github.com/mitchellrj/kamereon-python

The author of this project categorically rejects any and all responsibility related to vacuums managed by this integration.

## HACS Installation

1. Go to HACS
1. Add `github.com/alemuro/ha-nissan-connect` as a custom repository with category `Integration`
1. Install it

## Configure integration

1. Navigate to `Settings > Devices & Services` and then click `Add Integration`
1. Search for `Nissan Connect`
1. Enter your credentials

## Developers

### Local testing

If you already have a Nissan, I encourage you to test it by executing the `test.py`.

1. Install dependencies throuhg `pipenv`. Execute `pipenv install`.
1. Open virtualenv: `pipenv shell`.
1. Create a `.env` file with the variables `NISSAN_USERNAME`, `NISSAN_PASSWORD` and `VIN` (serial number). The serial number is retrieved by the script.
1. Execute `python test.py`.

There is a Makefile target to start a Docker container with this integration installed as a `custom_component`. Execute `make test-local`. This will create a local folder `.config`. To set debugging mode add this to `.config/configuration.yaml` file:

```
logger:
  default: info
  logs:
    custom_components.nissan_connect: debug
```

## Legal notice

This is a personal project and isn't in any way affiliated with, sponsored or endorsed by Nissan.

All product names, trademarks and registered trademarks in (the images in) this repository, are property of their respective owners. All images in this repository are used by the project for identification purposes only.
