TornadoWebReportsTango Device Server
==================================

Author(s): Daniel Roldan Ballesteros (droldan@cells.es)

Description: Tango device server to manage the a tornado Web Server and generate
 web reports from Tango Attributes

PROPERTIES
----------

Port (8888): Defines the port to Tornado access

AutoGenerateJSON: (True) or False, define if is necessary to create a JSON files 
with the last data.
The JSON files will be available in http://HOST/JSONfiles/(section).json

StructureConfig (DO NOT TOUCH) is the web report 'configuration' saved in a 
tango DDBB, so use internally, it is modified on save the configuration via web.
