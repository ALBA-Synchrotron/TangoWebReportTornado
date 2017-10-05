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

import sys
from PyTango import Util, DevFailed

# Import your devices class(es) here
from device import WebTornadoDS, WebTornadoDS4Impl

# Define your server name here
SERVER_NAME = 'WebTornadoDS'


# Main function that run the server
def run(args=None):
    try:
        if not args:
            args = sys.argv[1:]
            args = [SERVER_NAME] + list(args)

        print 'running server with args: %s' % repr(args)
        util = Util(args)
        util.add_class(WebTornadoDS, WebTornadoDS4Impl)
        U = Util.instance()
        U.server_init()
        U.server_run()

    except DevFailed, e:
        print '-------> Received a DevFailed exception:', e
    except Exception, e:
        print '-------> An unforeseen exception occurred....', e

if __name__ == '__main__':
    run()
