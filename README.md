# upc_connect_v2

This is a patched version of the original [`upc_connect`](https://www.home-assistant.io/integrations/upc_connect/) component with the added support for new Connect Box software versions (2022+).

## Installation

This is a custom component that you can manually install by copying the files from this repository to a `custom_components` folder.

## Configuration

Example `configuration.yaml` entry:

```yaml
device_tracker:
  - platform: upc_connect_v2
    host: 192.168.0.1
    username: admin
    password: PASSWORD
    legacy_mode: False
    encrypt_password: False
```

Variables:

|parameter|description|type|required|default|
---|---|---|:---:|---
`password` | The password of your router. | string | :white_check_mark: |
`username` | The username for your router. | string | :white_large_square: | admin
`host` | The IP address of your router. | string | :white_large_square: | 192.168.0.1
`legacy_mode` | Legacy authentication mode is used by older Connect Box software, by passing the authentication token as url parameter. Newer software (2022+) uses a cookie-based authentication. | boolean | :white_large_square: | True
`encrypt_password` | Configuration parameter for newer Connect Box software, where the `password` is sha256 encrypted. Setting this parameter to `True` will mean that the integration will encrypt the password you configured. If you prefer to encrypt the password yourself, set this to `False` | boolean | :white_large_square: | True
