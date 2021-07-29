import sys, os, threading, time
from datetime import datetime
from django.core.management.base import BaseCommand
from optparse import make_option
import socketserver  # python 3.x: socketserver, 2.x : SocketServer

from arduino_server import models


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        print("Got connection")

        data_received = ""  # Store data from network
        last_count_inserted = {}  # Buffer for latest values received from each meter

        while True:
            time.sleep(0.1)
            self.data = self.request.recv(1024).strip()
            data_received += self.data.decode('utf-8')
            if len(data_received) < 3:
                continue
            print("Received connection from %s" % str(self.client_address[0]))
            print("Data received: %s" % data_received)

            # Split values at our termination character
            values_received = data_received.split(";")

            # Secure against data overflow / dos attacks
            # In case we get too much data, just drop the connection
            # if len(data_received) > 5000:
            #    return

            # If we have not concluded receiving
            if not values_received or not "" == values_received[-1]:
                continue

            # Throw away empty stuff, return type fliter
            values_received = filter(lambda x: x != "", values_received)
            # Split by ":"
            values_received = dict(map(lambda x: x.split(":"), values_received))

            # Sort values so we start with the smallest ones
            try:
                value = ""
                values_received = sorted(values_received.items(), key=(lambda x: x[1]))
                # for key in values_received.keys():
                #     value = key + ':' + values_received[key] + ';'

                print(values_received)
                # values_received = value
                # values_received = sorted(values_received, key=lambda x: x[1], reverse=True)
                # print('value_recevied2', type(values_received), values_received)

            except IndexError:
                print("Value not correctly encoded (d:d; e.g. 1:1;)")
                continue

            # Iterate the values
            for meter_id, meter_count in values_received:
                try:

                    meter = models.Meter.objects.get(id=int(meter_id))

                    meter_count = float(meter_count)
                    print(meter, meter_id, meter_count)
                    # Factor in some fraction to the unit that the meter has specified.
                    meter_count = meter_count

                    # Check if we have a cached value - if not, find latest entry in database
                    if not last_count_inserted.get(meter_id, None):

                        # Find the latest data received in database
                        latest_data = models.MeterData.objects.filter(meter=meter).order_by('-id')

                        if latest_data:
                            last_count_inserted[meter_id] = latest_data[0].data_point
                        else:
                            last_count_inserted[meter_id] = 0

                    # If database counter is ahead, then the meter must have been reset
                    if meter_count < last_count_inserted[meter_id]:
                        insert_count = meter_count
                        diff = meter_count

                    # If meter is ahead of database, then the server must have been resting
                    else:
                        insert_count = meter_count
                        diff = meter_count - last_count_inserted[meter_id]

                    # Insert data
                    print("Inserting value %f - received value %f - diff: %f" % (insert_count, meter_count, diff))
                    data = models.MeterData(data_point=insert_count,
                                            meter=meter,
                                            created=datetime.now(),
                                            diff=diff * meter.unit_fraction)

                    data.save()

                    # Store values
                    last_count_inserted[meter_id] = meter_count

                except ValueError:
                    print("Not an integer", meter_id, meter_count)
                    return
                except IndexError:
                    print("No meter value received -- must be ID:VALUE")
                    continue
                except models.Meter.DoesNotExist:
                    print("No meter with this ID", meter_id)
                    continue

            data_received = ""

    def finish(self):
        print("Connection closed")
        return socketserver.BaseRequestHandler.finish(self)


class Command(BaseCommand):
    # args = '--dummy'
    help = 'Runs a server that listens to the arduino'  # @ReservedAssignment

    # option_list = BaseCommand.option_list + (
    #     make_option('--daemon', '-d', dest='daemon', default=False,
    #                 action='store_true',
    #                 help='Rum in daemon mode'),
    #     make_option('--pid-file', action='store', dest='pid',
    #                 default="c://temp//powermeterdaemon.pid",
    #                 help='Specify a file to put our process ID in (for daemon mode)'),
    #     make_option('--addr', action='store', dest='addr',
    #                 default="localhost",
    #                 help='Specify the ip address to listen to.'),
    #     make_option('--port', '-p', action='store', dest='port',
    #                 default="9999",
    #                 help='Specify a TCP port for listening.'),
    # )

    def add_arguments(self, parser):

        parser.add_argument(
            '--daemon',
            dest='daemon',
            action='store_true',
            default=False,
            help='Rum in daemon mode')

        parser.add_argument(
            '--pid-file',
            type=str,
            dest='pid',
            action='store',
            default='c://temp//powermeterdaemon.pid',
            help='Specify a file to put our process ID in (for daemon mode)')

        parser.add_argument(
            '--addr',
            type=str,
            dest='addr',
            action='store',
            default='localhost',
            help='Specify the ip address to listen to.')

        parser.add_argument(
            '--port',
            type=str,
            dest='port',
            action='store',
            default='9999',
            help='Specify a TCP port for listening.')

    def handle(self, *args, **options):

        daemon = options['daemon']
        pid_file_name = options['pid']
        addr = options['addr']
        port = int(options['port'])

        HOST, PORT = addr, port

        # Run as daemon, ie. fork the process
        # TODO: Make this a proper daemon mode following python standards...
        if daemon:
            fpid = os.fork()
            if fpid != 0:
                # Running as daemon now. PID is fpid
                with open(pid_file_name, "w") as pid_file:
                    pid_file.write(str(fpid))
                    sys.exit(0)

        # Create the server, binding to localhost on port 9999

        # socketserver.TCPServer.allow_reuse_address = True
        server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)

        server_thread = threading.Thread(target=server.serve_forever, args=())
        server_thread.setDaemon(True)
        server_thread.start()

        while True:
            try:
                print("Running server")
                time.sleep(20)
            except:
                print("Quitting server")
                server.server_close()
                sys.exit(1)
