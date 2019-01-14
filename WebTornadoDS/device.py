# *********************************************************************
# ESP8266ARS: Python project for a Tornado webServer and gen JSON
#
# Author(s): Daniel Roldan
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


import PyTango
import datetime
import fandango as fn
import fandango.tango as ft
import json
import math
import os
import shutil
import socket
import threading
import time
from matplotlib import cm
import numpy as np
import tornado
from PIL import Image
import Queue

from fandango import DynamicDS, DynamicDSClass, Cached, SortedDict
from tornado_app import TornadoManagement, TangoDSSocketHandler


class WebTornadoDS(DynamicDSClass):

    device_property_list = {'AutoGenerateJSON': [PyTango.DevBoolean,
                                                 'Auto Generate JSON files '
                                                 'for each section', False],

                            'port': [PyTango.DevLong, 'Tornado Port', 8888],

                            'WebFilesPath': [PyTango.DevString,
                                             'Location for main WebFiles', ""],

                            'extraJSONpath': [PyTango.DevString,
                                              'Extra location to save JSON '
                                              'files', None],

                            'structureConfig': [PyTango.DevString,
                                                'Internal register to save '
                                                'configuration, do not edit!',
                                                "{}"],

                            }
    device_property_list.update(DynamicDSClass.device_property_list)

    cmd_list = {

        'Start': [[PyTango.ArgType.DevVoid, 'Start listen detector to '
                                            'postprocess new images.'],
                  [PyTango.ArgType.DevVoid, '']],

        'Stop': [[PyTango.ArgType.DevVoid, 'Stop.'],
                 [PyTango.ArgType.DevVoid, '']],
        'Run': [[PyTango.ArgType.DevVoid, 'Run the refresh data'],
                [PyTango.ArgType.DevVoid, '']]

    }
    cmd_list.update(DynamicDSClass.cmd_list)

    attr_list = {
                'Url': [[PyTango.ArgType.DevString,
                        PyTango.AttrDataFormat.SCALAR,
                        PyTango.AttrWriteType.READ]],
                'extraJSONpath': [[PyTango.ArgType.DevString,
                                   PyTango.AttrDataFormat.SCALAR,
                                   PyTango.AttrWriteType.READ_WRITE],
                                  {'Memorized': 'True'}
                                  ],
                }

    attr_list.update(DynamicDSClass.attr_list)

    def __init__(self, name):
        super(WebTornadoDS, self).__init__(name)
        self.set_type("WebTornadoDS")
        print('In WebTornadoDS.__init__')


class WebTornadoDS4Impl(DynamicDS):

    JSON_FOLDER = 'JSONfiles/'
    DEFAULT_REFRESH_PERIOD = 3000

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
        self.get_device_properties(self.get_device_class())
        self.info_stream('In WebTornadoDS.__init__')
        self.set_state(PyTango.DevState.ON)
        self.tornado = TornadoManagement(port=self.port, parent=self)
        self.url = socket.gethostname() + ':' + str(self.port)
        self._data_dict = {}
        self.extraJSONpath = ""
        self._structureConfig = SortedDict()
        self.sem = threading.Semaphore()
        self.lock_read_structure_config = threading.Lock()
        self.force_acquisition = False
        self.last_refresh = {}
        self.is_reading_section = []
        self.last_refresh_section = 0
        self.acquisitionThread = None
        self.last_sections = []
        self.taskQueue = TaskQueue(self, num_workers=5)
        WebTornadoDS4Impl.init_device(self)

    # ------------------------------------------------------------------
    #   Device destructor
    # ------------------------------------------------------------------
    def delete_device(self):
        self.info_stream('In %s::delete_device()' % self.get_name())

        try:
            self.Stop()
        except Exception as e:
            self.error_stream(e)
        self.info_stream('Leaving %s::delete_device()' % self.get_name())

    # ------------------------------------------------------------------
    #   Device initialization
    # ------------------------------------------------------------------
    def init_device(self):
        self.info_stream('In %s::init_device()' % self.get_name())
        DynamicDS.init_device(self)
        self.Start()

    def Init(self):
        self.info_stream('In %s::Init()' % self.get_name())

        # Force to reload the properties.
        self.needJSON(force=True)
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
        # self.debug_stream('In %s::always_executed_hook()' % self.get_name())
        DynamicDS.always_executed_hook(self)
        self.state_machine()

    # ------------------------------------------------------------------
    #   Cmd command
    # ------------------------------------------------------------------
    def Start(self):
        self.info_stream('In %s::Start()' % self.get_name())
        if not self.acquisitionThread or not self.acquisitionThread.is_alive():
            self.force_acquisition = True

            self.taskQueue.add_task(AcquireObject(self).read_attributes_values)
            self.acquisitionThread = acquisitionThread(self)
            self.acquisitionThread.start()

        if not self.tornado.isRunning():
            try:
                self.tornado.start()
            except Exception as e:
                self.info_stream("Error on start Tornado: %r" % e)

    def Stop(self):
        self.info_stream('In %s::Stop()' % self.get_name())
        self.set_state(PyTango.DevState.ON)
        self.set_status('Status is ON')
        self.info_stream('Stop tornado')
        self.tornado.stop()
        self.info_stream('Stop acquisition thread')
        self.acquisitionThread.stop()
        self.taskQueue.stop()

    def GetAttributes(self):
        self.debug_stream(dir(self))
        self.debug_stream(self.dyn_attrs)
        self.debug_stream(self.dyn_values)
        self.debug_stream(self.dyn_comms)

    def read_extraJSONpath(self, the_att):
        self.info_stream('%s' % self.extraJSONpath)
        the_att.set_value(self.extraJSONpath)

    def write_extraJSONpath(self, attr):
        val = attr.get_write_value()
        self.extraJSONpath = val


    @Cached(depth=10, expire=3.)
    def getStructureConfig(self):
        try:
            pr = 'StructureConfig'
            p = self._db.get_device_property(self.get_name(), [pr])[pr][0]
            p = p.replace("'", "\"")
        except:
            p = '{}'

        config = json.loads(p)
        return config

    def setStructureConfig(self, conf):
        p = 'StructureConfig'
        try:
            self._db.put_device_property(self.get_name(), {p: conf})
        except Exception as e:
            print 'Exception on setStructureConfig'
            print e

        # Clean the last refresh dict to update ASAP
        self.last_refresh.clear()
        self.force_acquisition = True

    def getSections(self):

        if time.time() - self.last_refresh_section >= 1 or \
                self.force_acquisition:
            try:
                pr = 'StructureConfig'
                p = self._db.get_device_property(self.get_name(), [pr])[pr][0]
            except:
                return {}
            json_acceptable_string = p.replace("'", "\"")
            p = json.loads(json_acceptable_string)
            self._structureConfig.clear()
            self._structureConfig.update(p)
            self.last_refresh_section = time.time()

        return self._structureConfig

    def needJSON(self, force=False):

        if force:
            pr = 'AutoGenerateJSON'
            try:
                v = self._db.get_device_property(self.get_name(), [pr])[pr][0]
                self.AutoGenerateJSON = v
                # Eval Boolean String
                self.AutoGenerateJSON = eval(self.AutoGenerateJSON)

            except:
                self.AutoGenerateJSON = False
                self._db.put_device_property(self.get_name(),
                                             {pr: self.AutoGenerateJSON})
            pr = 'extraJSONpath'
            try:
                v = self._db.get_device_property(self.get_name(), [pr])[pr][0]
                self.extraJSONpath = v
            except:
                self.extraJSONpath = None

        return self.AutoGenerateJSON

    def readAttributesFromSection(self, section):
        attrs = []
        self._data_dict = {}

        # Read the current configuration.
        config = self.getStructureConfig()
        if section in config:
            for att in config[section]['Data']:
                attrs.append(att.lower())
        return attrs

    def Run(self):
        self.info_stream('RUN -> Force Acquisition')
        self.force_acquisition = True

    def checkAcquire(self):
        waiters = len(TangoDSSocketHandler.waiters)
        if self.needJSON() or waiters >= 1 or self.force_acquisition:
            sections = self.getSections()
            sections_keys = sections.keys()

            for section in sections_keys:
                try:
                    refresh_period = self._structureConfig[section][
                        'RefreshPeriod']
                except:
                    refresh_period = self.DEFAULT_REFRESH_PERIOD

                try:
                    full_name_section = sections[section]['fullname']
                except:
                    full_name_section = section

                if section in self.last_refresh:
                    t = time.time() - self.last_refresh[section]
                    t *= 1000
                    if (t >= refresh_period or self.force_acquisition) and \
                            section not in self.is_reading_section:
                        self.is_reading_section.append(section)
                        self.taskQueue.add_task(AcquireObject(self).acquire, section, full_name_section)
                        #self.acquire(section, full_name=full_name_section)
                else:
                    if section not in self.is_reading_section:
                        self.debug_stream('First refresh of %r' % section)
                        self.is_reading_section.append(section)

                        self.taskQueue.add_task(AcquireObject(self).acquire,
                                                section, full_name_section)

            # if extraJSONpath is enabled, create a simple json file with
            # the section active.
            if self.extraJSONpath and (self.last_sections != sections_keys):
                self.writeSectionsFile(sections)

            self.last_sections = sections_keys
        else:
            pass
            # print "WEB Data file  generation Stopped!!!...."
        self.force_acquisition = False

    def writeSectionsFile(self, sections):
        file = 'sections.json'
        sec = {}
        sec['sections'] = sections
        full_file = os.path.join(self.extraJSONpath, file)
        if not os.path.exists(os.path.dirname(full_file)):
            try:
                os.makedirs(os.path.dirname(full_file))
            except OSError as exc:  # Guard against race condition
                self.debug(exc)
                raise
        try:
            json.dump(sec, open(full_file, 'w'))
        except Exception as e:
            print e

        index_sections_file = os.path.join(self.extraJSONpath, 'index.html')
        dirname, filename = os.path.split(os.path.abspath(__file__))
        f = os.path.join(dirname, 'templates/index_of_sections.html')
        print "copy %r to %r\n\n" %(f, index_sections_file)
        try:
            shutil.copy(f, index_sections_file)
        except Exception as e:
            print e

    def newClient(self, client):
        self.last_refresh = {}
        json_data = {}

        # Config Json as a config
        json_data['command'] = 'config'

        # check if the property is empty
        # Read Current Attr Values
        att_values, config = AcquireObject(self).read_attributes_values()
        json_data['data'] = att_values
        json_data['host'] = tornado.httpserver.socket.gethostname()
        json_data['config'] = {}
        if config != '':
            json_data['config'] = config

        # Send Package
        client.write_message(json_data)
        client_name = client.request.remote_ip
        self.debug_stream("Main data contents refresh in client " + str(
            client_name))

    @PyTango.DebugIt()
    def read_Url(self, the_att):
        the_att.set_value(self.url)

    def attributes2json(self, folder, filename, attrs, keep=False, log=False):
        data_file = os.path.join(folder, filename)
        tmp_file = os.path.join(folder, 'temp.tmp')

        if not fn.isMapping(attrs):
            log = True
            attrs = self.attrs2dict(attrs, keep=keep, log=log)
        try:
            if not os.path.exists(os.path.dirname(data_file)):
                try:
                    os.makedirs(os.path.dirname(data_file))
                except OSError as exc:  # Guard against race condition
                    raise
            try:
                with open(tmp_file, 'w') as outfile:
                    json.dump(attrs, outfile)
                shutil.copyfile(tmp_file, data_file)
            except Exception as e:
                print e
            html_file = os.path.join(folder, 'index.html')
            dirname, filename = os.path.split(os.path.abspath(__file__))
            f = os.path.join(dirname, 'templates/index_single_section.html')
            try:
                shutil.copy(f, html_file)
            except Exception as e:
                print e
            # print('%d attributes written to %s'%(len(attrs),file))
        except Exception, e:
            print('attributes2json(%s) failed!' % data_file)
            failed = 0
            for k, v in sorted(attrs.items()):
                try:
                    json.dumps({k: v}, encoding='latin-1')
                except Exception, ee:
                    failed = 1
                    print((k, 'cannot be parsed: ', ee))
            if not failed:
                raise e
        return attrs

    def createImage(self, value, full_name, section=None):

        try:
            cmap = cm.get_cmap('jet')
            im = cmap(value)
            im = np.uint8(im * 255)
            img = Image.fromarray(im)
            image_name = full_name.replace('/', '_')
            image_name += ".jpg"
            # Save image in the server folder
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(curr_dir, self.JSON_FOLDER, section,
                                    image_name)
        except Exception as e:
            self.error_stream('Exception on compose the image %r' % e)
        try:
            img.save(img_path)
            self.debug_stream('Saved %r image' % img_path)

        except Exception as e:
            self.error_stream("Error on Save image in %r" % img_path)
            self.error_stream(e)

        try:
            if self.extraJSONpath:
                folder = self.extraJSONpath
                if section:
                    folder = os.path.join(folder, section)

                if not os.path.exists(folder):
                    os.makedirs(folder)

                img_path_ext = os.path.join(folder, image_name)
                img.save(img_path_ext)
                self.debug_stream('Saved %r image in %r' % (image_name,
                                                            folder))
        except Exception as e:

            msg = "Error on write Image to extraJSONpath: %r, " \
                  "%r" % (img_path_ext, e)
            self.error_stream(msg)

        return image_name

    def createJsonData(self, att_vals, section):
        val = {}
        val['data'] = att_vals
        time_now = datetime.datetime.fromtimestamp(
            time.time()).strftime('%Y-%m-%d %H:%M:%S')
        val['timestamp'] = time_now
        try:
            rp = self._structureConfig[section]['RefreshPeriod']
            val['refreshperiod'] = rp
        except:
            val['refreshperiod'] = self.DEFAULT_REFRESH_PERIOD
        val['section'] = section
        val['description'] = self._structureConfig[section]['Description']
        return val

    def get_dev_name(self, model):
        if ':' in model:
            model = model.split(':')[-1].split('/', 1)[-1]
            model = model.split('#')[0].strip('/')
        if model.count('/') > 2:
            model = model.rsplit('/', 1)[0]
        return model


class acquisitionThread(threading.Thread):
    def __init__(self, ds):
        threading.Thread.__init__(self)
        self.ds = ds
        self.stopped = False

    def run(self):
        while not self.stopped:
            time.sleep(1)
            self.ds.checkAcquire()

    def stop(self):
        self.stopped = True
        self.join()

class TaskQueue(Queue.Queue):

    def __init__(self, obj, num_workers=5):
        Queue.Queue.__init__(self)
        self.obj = obj
        self.stop = False
        self.num_workers = num_workers
        self.start_workers()

    def add_task(self, task, section=None, *args, **kwargs):
        #self.obj.debug_stream('Adding new Task por section %r' %repr(section))
        args = args or ()
        kwargs = kwargs or {}
        self.put((task, args, kwargs))

    def start_workers(self):
        for i in range(self.num_workers):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()

    def worker(self):
        while not self.stop:
            item, args, kwargs = self.get()
            item(*args, **kwargs)
            self.task_done()

    def stop(self):
        self.stop = True



class AcquireObject(object):
    def __init__(self, ds, recursive=False):
        self.ds = ds
        if not recursive:
            self._data_dict = SortedDict()

    def acquire(self, section, full_name=None):

        try:
            t = time.time()
            att_vals = []
            try:
                att_vals, config = self.read_attributes_values(section)
                jsondata = {}
                jsondata['config'] = config
                jsondata['command'] = 'update'
                jsondata['data'] = att_vals
                jsondata['section'] = section
                jsondata['section_full_name'] = full_name
                utime = time.strftime("%Y-%m-%d %H:%M:%S",
                                      time.localtime())
                jsondata['updatetime'] = utime
            except Exception as e:
                print e
                self.ds.error_stream('Exception on complete the jsondata')
                self.ds.error_stream(str(e))

            # check if the data is empty:
            if len(att_vals) != 0:
                if self.ds.AutoGenerateJSON:
                    try:
                        dir_path = os.path.dirname(
                            os.path.realpath(__file__))

                        folder = os.path.join(dir_path,
                                              self.ds.JSON_FOLDER,
                                              section)
                        filename = "data.json"

                        val = self.ds.createJsonData(att_vals, section)
                        self.ds.debug_stream('Saving json in %r' % folder)
                        self.ds.attributes2json(folder, filename, val)
                    except Exception as e:
                        self.ds.debug_stream("Error on create JSON file in %r "
                                          "\n %r" % (folder, e))
                    try:
                        if self.ds.extraJSONpath:
                            filename = "data.json"
                            folder = os.path.join(self.ds.extraJSONpath,
                                                  section)
                            val = self.ds.createJsonData(att_vals,
                                                      section)
                            self.ds.debug_stream('Saving json in %r' % folder)
                            self.ds.attributes2json(folder, filename, val)
                    except Exception as e:
                        msg = "Error on write extraJSONpath: %r" % e
                        self.ds.error_stream(msg)
                # Sent generated data to clients
                for waiter in TangoDSSocketHandler.waiters:
                    try:
                        waiter.write_message(jsondata)
                    except:
                        self.ds.error_stream("Error sending message to "
                                          "waiters...")

            if section in self.ds.last_refresh:
                t = time.time() - self.ds.last_refresh[section]
            else:
                t = time.time() - t
            self.ds.info_stream("Refresh %r with %r seconds\n" % (section, t))
            self.ds.last_refresh[section] = time.time()
            self.ds.is_reading_section.remove(section)


        except Exception as e:
            self.ds.error_stream('Exception in acquire method: %r' % e)

    def read_attributes_values(self, filter_by_section=None):
        # Check current config
        attrs = []
        t0 = time.time()
        # Read the current configuration.
        config = self.ds.getStructureConfig()
        sections_rel = {}
        # Get Sections info
        if filter_by_section is not None:
            sections = [filter_by_section]
        else:
            sections = config.keys()
            for section in sections:
                d, config = self.read_attributes_values(section)
                self._data_dict.update(d)
            return self._data_dict, config

        for section in sections:

            if section not in config:
                self.ds.error_stream('ERROR: Section %r not found in config %r'
                                  % (section, config))
                continue

            for att in config[section]['Data']:
                att = att.lower()
                attrs.append(att)
                sections_rel[att] = section
        _data_dict = {}
        internal_attrs = []
        external_attrs = []
        # Add info in a dict for each attribute
        for full_name in attrs:

            full_name = str(full_name).lower()
            _data_dict[full_name] = {}

            try:
                dev_name = self.ds.get_dev_name(full_name)

                if dev_name == self.ds.get_name():
                    attr = full_name.split('/')[-1]
                    a = ft.read_internal_attribute(self, attr).read()
                    internal_attrs.append(a)
                else:
                   # a = ft.CachedAttributeProxy(full_name,
                   # use_gevent=True).read()
                    a = ft.CachedAttributeProxy(full_name).read()
                    #a = fn.EventSource(full_name,
                    #                  enablePolling=10000,
                    #                  tango_asynch=True,
                    #                  persistent=True)
                    external_attrs.append(a)


                if a.data_format == PyTango.AttrDataFormat.IMAGE:
                    _data_dict[full_name]['data_format'] = "IMAGE"
                    # VALUE should be the image path
                    # value = array2Image(value, 'jpeg')

                    try:
                        if self.ds.AutoGenerateJSON:
                            image_name = self.ds.createImage(a.value,
                                                             full_name,
                                                          section)
                    except Exception as e:
                        self.ds.error_stream('Exception on create Image, '
                                            '%r' % e)
                        # TODO: add default image in case of error
                        image_name = 'template.jpg'
                    value = image_name

                elif ft.isSequence(a.value):
                    if type(a.value) is tuple:
                        value = list(a.value)
                    else:
                        value = a.value.tolist()
                    _data_dict[full_name]['data_format'] = "SPECTRUM"
                else:
                    # Check Tango States
                    if a.value in PyTango.DevState.values:
                        value = str(a.value)
                    else:
                        value = a.value
                    _data_dict[full_name]['data_format'] = "SCALAR"
                    try:
                        if math.isnan(value):
                            value = '---'
                    except:
                        pass

                _data_dict[full_name]['value'] = value
                _data_dict[full_name]['quality'] = str(a.quality)
                _data_dict[full_name]['full_name'] = full_name
                _data_dict[full_name]['label'] = str(a.name)
                _data_dict[full_name]['section'] = sections_rel[full_name]
            except Exception as e:
                # return an error for this attribute in Exception case
                _data_dict[full_name]['data_format'] = "SCALAR"
                _data_dict[full_name]['value'] = "Attr not found"
                _data_dict[full_name]['quality'] = "ATTR_NOT_FOUND"
                _data_dict[full_name]['full_name'] = full_name
                _data_dict[full_name]['label'] = full_name
                _data_dict[full_name]['section'] = sections_rel[full_name]
                self.ds.error_stream('%s failed!' % full_name)
                self.ds.error(e)

        return _data_dict, config
