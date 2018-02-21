import resource
import update
import socketserver, threading, sys, pickle
from threaded_tcp_server import ThreadedTCPServer

resources = {}

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # I CAN HANDLE MYSELF OKAY
        self.data = self.request.recv(1024).strip()
        print("Processing data from client {} in thread {}".format(
                self.client_address[0],
                threading.current_thread().name
            )
        )
        decoded = pickle.loads(self.data)
        print(decoded)
        r, u = None, None
        try:
            r = resource.Resource(decoded[0]["label"], decoded[0]["serial_no"], decoded[0]["key"], None)
            u = update.Update(r, decoded[1], decoded[0]["value"])
        except KeyError:
            # recieved malformed dict
            print("Malformed dict from {}!".format(self.client_address[0]))
        print("Decoded pickle into update object and resource object")
        u.update_resource()
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
                pass # HACK for Ctrl+C interrupt
        except KeyboardInterrupt:
            print("\nCaught Ctrl+C")
            print("Shutting down...")
            r_server.shutdown()
            r_server.setDB(resources)
            r_server.server_close()
            print("Server thread terminated. Note that the socket may take some time to unbind.")
            exit(0)

def start():
    main(str(sys.argv[1])) # server.start is more natural, this also allows us to make main() more complex

if __name__ == "__main__":
    start()

