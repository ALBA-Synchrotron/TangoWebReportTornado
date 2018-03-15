TornadoWebReportsTango Device Server
==================================

Author(s): Daniel Roldan Ballesteros (droldan@cells.es)

Description: Tango device server to manage a tornado Web Server and generate
 web reports from Tango Attributes.
 Also, allows to generate a Json files/images with the tango attrs defined in a specifing path or url.

PROPERTIES
----------

Port (8888): Defines the port to Tornado access

AutoGenerateJSON: (True) or False, define if is necessary to create a JSON files 
with the last data.
The JSON files will be available in http://HOST/JSONfiles/(section).json

extraJSONpath: empty by default, an extra path to save the Json/Images generated.

StructureConfig (DO NOT TOUCH) is the web report 'configuration' saved at 
tango DDBB, so use internally, it is modified on save the configuration via web.
