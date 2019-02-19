WebTornado Device Server
========================

Author(s): Daniel Roldan Ballesteros (droldan@cells.es)

Description: The WebTornadoDS Tango Device Server embeds a Tornado web
application into a Tango device.

When running on a given HOST; it will publish a webpage at
http://HOST:PORT showing the values of the configured attributes

These values are stored in .json files; that can be generated in a
different machine from the  one publishing the data.


PROPERTIES
----------

***Port***: (8888) Defines the port to Tornado access

***AutoGenerateJSON***: True or (False), define if is necessary to create a
JSON files with the last data.

- If *False*, data is updated only when a client connects to the
server:port
- If *True*, data is generated continuously

The JSON files will be available in http://HOST/(section).json

***extraJSONpath***: empty by default, an extra path to save the
JSON/Images generated, it can be used to copy the generated files to
an external server via NFS

Even if *extraJSONpath* has no value, the JSON files will be stored in
the device server folder and available in
http://HOST/JSONfiles/(section).json

***WebFilesPath*** : location for custom html files (machinestatus.html path)


***StructureConfig***: **(DO NOT TOUCH)** It is the web report
'*configuration*' saved at tango DB, so use internally, it is modified on save the
configuration via web.
