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
