## Checkbox and Manifest example
This is a example about how to implement an extra checkbox configuration and manifest for a specific system.

Assume that a system (CID number is 201212-12345) is a desktop and a serial add-on card is installed

### an extra checkbox configuration
As you can see from the extra_checkbox.conf, we hae to define the SERIAL_PORTS_STATIC for the serial interface tests

### Manifest JSON
As you can see from the manifest.json, we define the "has_camera" to false due to there is no camera interface for this system.