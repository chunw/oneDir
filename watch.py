from os.path import expanduser
import os
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests

# Configs
home = expanduser("~")
UPLOAD_FOLDER = home + '/uploads'  # assume client user has a dir called uploads under home dir
SERVER_URL = 'http://localhost:5000'


def upload_file_to_server(file_path):
    temp = file_path.split("uploads/")
    filename = temp[1]
    os.system("curl -X POST -F file=@" + file_path + " \"http://localhost:5000/\"")
  #  os.curl("-O http")
    os.system("curl -O \"http://127.0.0.1:5000/uploads/<filename>\" | ~/Desktop")
    print filename
    print file_path


class MyEventHandler(FileSystemEventHandler):
    """ customized file system event handler
        TODO ignore pattern in path: ".DS_Store"
    """
    def catch_all(self, event, op):
        op_file_path = event.src_path
        print (op, event.is_directory, op_file_path)

    def on_created(self, event):
        self.catch_all(event, 'NEW')
        if event.is_directory:
            upload_file_to_server(event.src_path)
        else:
            # TODO create folder on server
            return

    def on_deleted(self, event):
        self.catch_all(event, 'DEL')
        # TODO delete folder on server

    def on_modified(self, event):
        # Note: this event is also triggered with on_created or on_deleted event

        if event.is_directory:
            # Note for Mac OS X: FSEvents returns only the directory for file modified events,
            # which means event.is_directory is not reflecting the truth in Mac OS.

            # Detect the full path in Mac OS. TODO test in other OS.

            files_in_dir = [event.src_path+"/"+f for f in os.listdir(event.src_path)]
            op_file_path = max(files_in_dir, key=os.path.getmtime)
            upload_file_to_server(op_file_path)
        else:
            op_file_path = event.src_path
        print ("MOD", event.is_directory, op_file_path)


if __name__ == "__main__":

    # Format console logs.
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    # Start watchdog
    observer = Observer()
    event_handler = MyEventHandler()
    observer.schedule(event_handler, path=UPLOAD_FOLDER, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
