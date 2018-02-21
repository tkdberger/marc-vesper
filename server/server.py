import resource
import update
import util
import socketserver
import threading
import sys
import pickle
from threaded_tcp_server import ThreadedTCPServer

resources = {}


class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # I CAN HANDLE MYSELF OKAY
        self.data = self.request.recv(1024).strip()
        util.print_labeled(
            "Processing data from client {}".format(self.client_address[0]))
        decoded = pickle.loads(self.data)
        util.print_labeled("recieved key {}".format(decoded[0]["key"]))
        r, u = None, None
        try:
            r = resource.Resource(
                decoded[0]["label"], decoded[0]["serial_no"], decoded[0]["key"])
            u = update.Update(r, decoded[1], decoded[0]["value"], None)
        except KeyError:
            # recieved malformed dict
            util.print_labeled(
                "Malformed dict from {}!".format(self.client_address[0]))
        try:
            u.oldres = resources[decoded[0]["label"]]
        except KeyError:
            util.print_labeled("No old resource found!")
        util.print_labeled("Decoded pickle into update and resource objects.")
        if (u.update_resource()):
            resources[decoded[0]["label"]] = r.toDict()
        self.finish()


def main(address):
    print("Starting socketserver")
    with ThreadedTCPServer((address, 9999), TCPHandler) as r_server:
        try:
            server_thread = threading.Thread(target=r_server.serve_forever)
            # Exit the server thread when the main thread terminates
            server_thread.daemon = True
            server_thread.start()
            resources = r_server.getDB()
            print("Server loop running in thread:", server_thread.name)
            while True:
                pass  # HACK for Ctrl+C interrupt
        except KeyboardInterrupt:
            print("\nCaught Ctrl+C")
            print("Shutting down...")
            print(resources)
            r_server.setDB(resources)
            r_server.shutdown()
            r_server.server_close()
            print(
                "Server thread terminated. Note that the socket may take some time to unbind.")
            exit(0)


def start():
    # server.start is more natural, this also allows us to make main() more complex
    main(str(sys.argv[1]))


if __name__ == "__main__":
    start()
