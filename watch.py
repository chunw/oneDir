from os.path import expanduser
import os
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler

# Configs
home = expanduser("~")
UPLOAD_FOLDER = home + '/uploads'  # assume client user has a dir called uploads under home dir


class MyEventHandler(FileSystemEventHandler):
    """ customized file system event handler """

    def catch_all(self, event, op):

        if event.is_directory:
            return

        filename = event.src_path
        print (op, filename)

    def on_created(self, event):
        self.catch_all(event, 'NEW')
        # upload via curl

    def on_modified(self, event):
        self.catch_all(event, 'MOD')
        # upload via curl


if __name__ == "__main__":

    # Format console logs.
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    # Start watchdog
    #event_handler = MyEventHandler()
    event_handler = LoggingEventHandler() # default logging
    observer = Observer()
    observer.schedule(event_handler, path=UPLOAD_FOLDER, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
