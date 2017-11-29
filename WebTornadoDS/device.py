#*********************************************************************
# ESP8266ARS: Python project for a ALBA Remote Sensors base on ESP8266.
#
# Author(s): Roberto J. Homs Puron <rhoms@cells.es>,
#            Alberto Rubio Garcia <arubio@cells.es>
#            Sergio Astorga Sanchez <sastorga@cells.es>
#
# Copyright (C) 2017, CELLS / ALBA Synchrotron
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import json
import os
import socket
import time
import datetime
import PyTango
import fandango as fn
import fandango.tango as ft
import tornado
from fandango import DynamicDS, DynamicDSClass

from tornado_app import TornadoManagement, TangoDSSocketHandler
import taurus
from matplotlib import cm
import numpy as np
from PIL import Image
import shutil
import threading

class WebTornadoDS(DynamicDSClass):



    device_property_list = {
                            'AutoGenerateJSON': [PyTango.DevBoolean,
                                                 'Auto Generate JSON files '
                                                 'for each section', False ],
                            'port': [PyTango.DevLong, 'Tornado Port', 8888],
                            'WebFilesPath': [PyTango.DevString, 'Location main '
                                                                 'WebFiles', ""],

                            'extraJSONpath': [PyTango.DevString, 'extra '
                                                                 'location '
                                                                 'to save '
                                                                 'JSON '
                                                                 'files',
                                              ""]

    }
    device_property_list.update(DynamicDSClass.device_property_list)


    cmd_list = {

        'Start': [[PyTango.ArgType.DevVoid, 'Start listen detector to '
                                            'postprocess new images.'],
                  [PyTango.ArgType.DevVoid, '']],

        'Stop': [[PyTango.ArgType.DevVoid, 'Stop.'],
                 [PyTango.ArgType.DevVoid, '']],
        'Run': [[PyTango.ArgType.DevVoid, 'Run the refresh data'],
                  [PyTango.ArgType.DevVoid, ''],
                ]

    }
    cmd_list.update(DynamicDSClass.cmd_list)

    attr_list = {

                  'Url':[[PyTango.ArgType.DevString,
                              PyTango.AttrDataFormat.SCALAR,
                              PyTango.AttrWriteType.READ]],
                  'refresh_period': [[PyTango.ArgType.DevFloat,
                                      PyTango.AttrDataFormat.SCALAR,
                                      PyTango.AttrWriteType.READ_WRITE],
                                     {
                                        'Memorized': 'True',
                                        'unit': 'ms',
                                         'min_value': 100,
                                    }],
                  'extraJSONpath':[[PyTango.ArgType.DevString,
                              PyTango.AttrDataFormat.SCALAR,
                              PyTango.AttrWriteType.READ_WRITE],
                                    {
                                    'Memorized': 'True',
                                    }],
     }

    # #attr_list = {
    #
    #             'Folder': [[PyTango.ArgType.DevString,
    #                       PyTango.AttrDataFormat.SCALAR,
    #                       PyTango.AttrWriteType.READ_WRITE]],
    #             }
    attr_list.update(DynamicDSClass.attr_list)

    def __init__(self, name):
        print 'In WebTornadoDS.__init__'
        super(WebTornadoDS, self).__init__(name)
        self.set_type("WebTornadoDS")


class WebTornadoDS4Impl(DynamicDS):

    JSON_FOLDER = 'JSONfiles/'

    EMPTY_ATTR = {
        'alarms': [],
        'arch_event': [],
        'ch_event': [],
        'color': 'Grey',
        'data_format': 'SCALAR',
        'data_type': 'DevDouble',
        'database': '',
        'description': '',
        'device': '',
        'display_unit': '',
        'format': '',
        'label': '----',
        'max_alarm': '',
        'min_alarm': '',
        'model': '',
        'name': '---',
        'polling': '',
        'quality': 'ATTR_INVALID',
        'standard_unit': '',
        'string': '----',
        'time': time.time(),
        'unit': '',
        'value': None,
        'writable': 'READ',
    }

    # ------------------------------------------------------------------
    #   Device constructor
    # ------------------------------------------------------------------
    def __init__(self, cl, name):
        DynamicDS.__init__(self, cl, name)
        self.info_stream('In WebTornadoDS.__init__')
        WebTornadoDS4Impl.init_device(self)
        self.set_state(PyTango.DevState.ON)


    # ------------------------------------------------------------------
    #   Device destructor
    # ------------------------------------------------------------------
    def delete_device(self):
        self.info_stream('In %s::delete_device()' % self.get_name())

        try:
            self.Stop()
        except Exception as e:
            print e
        self.info_stream('Leaving %s::delete_device()' % self.get_name())

    # ------------------------------------------------------------------
    #   Device initialization
    # ------------------------------------------------------------------
    def init_device(self):
        self.info_stream('In %s::init_device()' % self.get_name())
        self.get_device_properties(self.get_device_class())

        DynamicDS.init_device(self)

        self.tornado = TornadoManagement(port=self.port, parent=self)
        self.url = socket.gethostname() + ':' + str(self.port)
        self._data_dict = {}
        self.refresh_period = 3000
        self.extraJSONpath = ""
        self.structureConfig = {}
        self.Start()
        self.sem = threading.Semaphore()

    def Init(self):
        self.info_stream('In %s::Init()' % self.get_name())
        self.Stop()
        self.Start()
    # ------------------------------------------------------------------
    #   State machine implementation
    # ------------------------------------------------------------------
    def state_machine(self):
        if self.tornado.isRunning():
            self.set_state(PyTango.DevState.RUNNING)
            self.set_status('Tornado is Running')

        else:
            self.set_state(PyTango.DevState.ON)
            self.set_status('Tornado is Stopped')

    # ------------------------------------------------------------------
    #   Always executed hook method
    # ------------------------------------------------------------------
    def always_executed_hook(self):
        self.debug_stream('In %s::always_executed_hook()' % self.get_name())
        DynamicDS.always_executed_hook(self)
        self.state_machine()

    # ------------------------------------------------------------------
    #   Cmd command
    # ------------------------------------------------------------------
    def Start(self):
        self.info_stream('In %s::Start()' % self.get_name())
        if not self.tornado.isRunning():
            try:
                self.tornado.start()
            except Exception as e:
                self.info_stream("Error on start Tornado: %r"%e)

    def Stop(self):
        self.info_stream('In %s::Stop()' % self.get_name())
        self.set_state(PyTango.DevState.ON)
        self.set_status('Status is ON')
        self.tornado.stop()

    def GetAttributes(self):
        print dir(self)
        print self.dyn_attrs
        print self.dyn_values
        print self.dyn_comms


    # ------------------------------------------------------------------
    #   read Attr attribute
    # ------------------------------------------------------------------

    def read_refresh_period(self, the_att):
        self.info_stream('%s' % self.refresh_period)
        U = PyTango.Util.instance()
        admin = U.get_dserver_device()
        val =  self.get_command_poll_period('Run')
        self.refresh_period = val
        the_att.set_value(self.refresh_period)

    def write_refresh_period(self, attr):
        val = attr.get_write_value()
        self.refresh_period = val
        self.poll_command('Run', int(self.refresh_period))

    def read_extraJSONpath(self, the_att):
        self.info_stream('%s' % self.extraJSONpath)
        the_att.set_value(self.extraJSONpath)

    def write_extraJSONpath(self, attr):
        val = attr.get_write_value()
        self.extraJSONpath = val

    def getStructureConfig(self):
        try:
            p = self._db.get_device_property(self.get_name(),['StructureConfig'])[
                'StructureConfig'][0]
        except:
            p = '{}'

        return p

    def setStructureConfig(self, conf):
        self._db.put_device_property(self.get_name(),
                                     {'StructureConfig':conf})

    def getSections(self):
        try:
            p = self._db.get_device_property(self.get_name(),['StructureConfig'])['StructureConfig'][0]
        except:
            return []
        json_acceptable_string = p.replace("'", "\"")
        p = json.loads(json_acceptable_string)
        self.structureConfig = p
        return p.keys()

    def needJSON(self):
        try:
            self.AutoGenerateJSON = self._db.get_device_property(
                self.get_name(),['AutoGenerateJSON'])['AutoGenerateJSON'][0]
            if self.AutoGenerateJSON == 'False':
                self.AutoGenerateJSON = False

        except:
            self._db.put_device_property(self.get_name(),
                                         {'extraJSONpath': self.AutoGenerateJSON})
            pass

        try:
            self.extraJSONpath = self._db.get_device_property(
                self.get_name(), ['extraJSONpath'])['extraJSONpath'][0]
        except:
            self._db.put_device_property(self.get_name(),
                                         {
                                             'AutoGenerateJSON': self.AutoGenerateJSON
                                         })
        return self.AutoGenerateJSON
        
    def readAttributesFromSection(self, section):
        attrs = []
        self._data_dict = {}

        # Read the current configuration.
        config = self.getStructureConfig()    
        json_acceptable_string = config.replace("'", "\"")
        config = json.loads(json_acceptable_string)   
        if section in config:
            for att in config[section]['Data']: 
                attrs.append(att.lower())
        return attrs    

    def Run(self):
        report_msg = False
        try:
            waiters = len(TangoDSSocketHandler.waiters)
            if self.needJSON() or waiters >= 1:

                sections = self.getSections()

                for section in sections:
                    att_vals = []
                    try:
                        att_vals = self.read_attributes_values(section)
                        jsondata = {}
                        jsondata['command'] = 'update'
                        jsondata['data'] = att_vals
                        jsondata['section'] = section
                        jsondata['updatetime'] = time.strftime("%Y-%m-%d %H:%M:%S",
                                                               time.localtime())
                    except Exception as e:
                        print e

                    # check if the data is empty:
                    if len(att_vals) != 0:
                        if self.AutoGenerateJSON:
                            dir_path = os.path.dirname(
                                os.path.realpath(__file__))

                            folder = os.path.join(dir_path,self.JSON_FOLDER,
                                                  section)
                            filename = "data.json"

                            val = self.createJsonData(att_vals, section)

                            self.attributes2json(folder,
                                                 filename, val)
                            try:
                                if self.extraJSONpath != "":
                                    filename = "data.json"
                                    folder = os.path.join(self.extraJSONpath,
                                                        section)
                                    val = self.createJsonData(att_vals, section)

                                    self.attributes2json(folder,
                                                         filename, val)
                            except Exception as e:
                                msg ="Error on write JSON to extraJSONpath: " \
                                     "%r"%e
                                print msg
                            # Sent generated data to clients
                        for waiter in TangoDSSocketHandler.waiters:
                            try:
                                waiter.write_message(jsondata)
                            except:
                                print "Error sending message to waiters...."
            else:
                if not report_msg:
                    print "WEB Data file  generation Stopped!!!...."
                    report_msg = True
        except Exception as e:
            print e

    def newClient(self, client):
        json_data = {}

        # Config Json as a config
        json_data['command'] = 'config'

        # Send the section Confit at first time
        conf = self.getStructureConfig()

        # check if the property is empty
        if conf != '':
            json_data['config'] = json.loads(conf)
        else:
            json_data['config'] = {}
        # Read Current Attr Values
        att_values = self.read_attributes_values()
        json_data['data'] = att_values
        json_data['host'] = tornado.httpserver.socket.gethostname()
        # Send Package
        client.write_message(json_data)
        client_name = client.request.remote_ip

        print "Main data contents refresh in client " + str(client_name)

    def read_attributes_values(self, filter_by_section=None):
        # Check current config
        self.sem.acquire()
        print "Entering in read_atttrbibutes_values"

        attrs = []
        self._data_dict = {}

        # Read the current configuration.
        config = self.getStructureConfig()
        json_acceptable_string = config.replace("'", "\"")
        config = json.loads(json_acceptable_string)

        sections_rel = {}

        # Get Sections info
        if filter_by_section:
            sections = [filter_by_section]
        else:
            sections = config.keys()

        for section in sections:
            for att in config[section]['Data']:
                att = att.lower()
                attrs.append(att)
                sections_rel[att] = section

        # Add info in a dict for each attribute
        for full_name in attrs:

            full_name = str(full_name).lower()
            self._data_dict[full_name] = {}

            try:
                print "Entering %r"%full_name
                # Read the Current Value / config
                import fandango.callbacks

                #a = fandango.callbacks.EventSource('test',
                #    force_polling=True,polling_period=3000.).read()
                import fandango.tango as ft
                #model = ft.parse_tango_model(full_name)
                #my_host = ft.get_tango_host().split(':')[0].split('.')[0]
                #self.info(' reading %s / %s' % (model.device,model.attribute) )
                a = taurus.Attribute(full_name)
                dev_name = a.getParentObj().getNormalName()
                if dev_name == self.get_name():
                    a = ft.read_internal_attribute(self,a.name).read()
                else:
                    a = PyTango.AttributeProxy(full_name).read()

                self.info(' reading %s, done' % full_name)
                #self._data_dict[full_name]['data_format'] = str(a.data_format)

                if a.data_format == PyTango.AttrDataFormat.IMAGE:
                    self._data_dict[full_name]['data_format'] = "IMAGE"
                    # VALUE should be the image path
                    # value = array2Image(value, 'jpeg')
                    # TODO: default image
                    imagename = 'template.jpg'
                    if self.AutoGenerateJSON:
                        imagename = self.createImage(a.value, full_name,
                                                     section)
                    value = imagename

                elif fandango.isSequence(a.value):
                    if type(a.value) is tuple:
                        value = list(a.value)
                    else:
                        value = a.value.tolist()
                    self._data_dict[full_name]['data_format'] = "SPECTRUM"
                else:
                    # Check Tango States
                    if a.value in PyTango.DevState.values:
                        value = str(a.value)
                    else:
                        value = a.value
                    self._data_dict[full_name]['data_format'] = "SCALAR"

                self._data_dict[full_name]['value'] = value
                self._data_dict[full_name]['quality'] = str(a.quality)
                self._data_dict[full_name]['full_name'] = full_name
                self._data_dict[full_name]['label'] = str(a.name)
                self._data_dict[full_name]['section'] = sections_rel[full_name]
            except Exception as e:
                # return an error for this attribute in Exception case
                self._data_dict[full_name]['data_format'] = "SCALAR"
                self._data_dict[full_name]['value'] = "Attr not found"
                self._data_dict[full_name]['quality'] = "ATTR_NOT_FOUND"
                self._data_dict[full_name]['full_name'] = full_name
                self._data_dict[full_name]['label'] = full_name
                self._data_dict[full_name]['section'] = sections_rel[full_name]
                print('%s failed!'%full_name)
                print e


        self.last_values_update = time.time()
        print "leaving in read_atttrbibutes_values"
        self.sem.release()
        return self._data_dict


    @PyTango.DebugIt()
    def read_Url(self, the_att):
        self.info_stream("read_url")
        the_att.set_value(self.url)


    def attrs2dict(self, attrs,keep=False,log=False):
        vals = {}
        failed = []
        devs = fn.dicts.defaultdict(list)
        [devs[a.rsplit('/',1)[0]].append(a) for a in attrs]

        for d,attrs in devs.items():
            if not ft.check_device(d):
              print('%s device is not running!'%d)
              for t in attrs:
                vals[t] = EMPTY_ATTR
                vals[t]['model'] = t
                vals[t]['label'] = vals[t]['name'] = t.rsplit('/')[-1]
                vals[t]['device'] = d
            else:
              for t in attrs:
                try:
                  v = ft.export_attribute_to_dict(t)
                  if log: print(v['model'],v['string'])
                  if v['value'] is None:
                    v['color'] = 'Grey'
                    v['string'] = '...'
                  elif fn.isSequence(v['string']):
                    sep = '\n' if v['data_type'] == 'DevString' else ','
                    v['string'] = sep.join(v['string'])
                  v['string'] = unicode(v['string'],'latin-1')
                  v['tooltip'] = v['model'] + ':' + v['string']
                  try:
                    json.dumps(v)
                  except:
                    if log: print('json.dumps(%s) failed'%t)
                    if fn.isSequence(v['value']):
                      v['value'] = list(v['value'])
                    if fn.isBool(v['value']):
                      v['value'] = bool(v['value'])
                  vals[v['model']] = v
                except:
                  if log:
                    print('export_attribute_to_dict(%s) failed'%t)
                    #
                  vals[t] = None
                  failed.append(t)
        if failed:
            print('%d failed attributes!: %s'%(len(failed),' '.join(failed)))
        return vals

    def attributes2json(self, folder, filename, attrs,keep=False,log=False):
        file = os.path.join(folder, filename)

        if not fn.isMapping(attrs):
          attrs = self.attrs2dict(attrs,keep=keep,log=log)
        try:
          if not os.path.exists(os.path.dirname(file)):
              try:
                  os.makedirs(os.path.dirname(file))
              except OSError as exc: # Guard against race condition
                  raise
          json.dump(attrs,open(file,'w'),encoding='latin-1')
          html_file = os.path.join(folder, 'index.html')
          dirname, filename = os.path.split(os.path.abspath(__file__))
          file = os.path.join(dirname, 'templates/index_section.html')
          shutil.copy(file, html_file)
          print('%d attributes written to %s'%(len(attrs),html_file))
        except Exception,e:
          print('attributes2json(%s) failed!'%file)
          failed = 0
          for k,v in attrs.items():
            try:
              json.dumps({k:v},encoding='latin-1')
            except Exception,ee:
              failed = 1
              print((k,'cannot be parsed: ',ee))
          if not failed:
              raise e
        return attrs
        

    def createImage(self, value, full_name, section=None):
        map = cm.get_cmap('jet')
        im = map(value)
        im = np.uint8(im * 255)
        img = Image.fromarray(im)

        imagename = full_name.replace('/','_')
        imagename =  imagename + ".jpg"

        imagenamepath = os.path.join(self.extraJSONpath, imagename)

        img.save(imagenamepath)

        try:
            if self.extraJSONpath != "":
                folder = self.extraJSONpath
                if section:
                    folder = os.path.join(self.JSON_FOLDER, section)

                imagenamepathext = os.path.join(folder,
                                    imagename)
                img.save(imagenamepathext)
        except Exception as e:
            msg = "Error on write Image to extraJSONpath: " \
                  "%r" % e
            print msg

        return imagename
    def createJsonData(self, att_vals, section):
        val = {}
        val['data'] = att_vals
        time_now = datetime.datetime.fromtimestamp(
            time.time()).strftime('%Y-%m-%d %H:%M:%S')
        val['timestamp'] = time_now
        val['refresh_period'] = self.refresh_period
        val['section'] = section
        val['description'] = self.structureConfig[section]['Description']
        return val