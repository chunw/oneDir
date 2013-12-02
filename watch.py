__author__ = 'Chun'

from os.path import expanduser
import os
import sys
import time
import logging
import main
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

# configs
home = expanduser("~")
UPLOAD_FOLDER = home + '/onedir'  # assume client user has a dir called uploads under home dir

class MyEventHandler(FileSystemEventHandler):
    """ customized file system event handler
    """

    def __init__(self, client_name, server_url):
        super(FileSystemEventHandler, self).__init__()
        self.clientName = client_name
        self.serverUrl = server_url
        self.ignore_pattern = ".DS_Store"

    def catch_all(self, event, op):
        if not self.ignore_pattern in event.src_path:
            print (op, event.src_path)

    def parse_filename(self, file_path):
        temp = file_path.split("onedir/")
        return temp[1]

    def on_created(self, event):
        # event.is_directory is correct
        self.catch_all(event, 'NEW')
        filename = self.parse_filename(event.src_path)
        main.clientUpload(filename, self.clientName)
        main.update_db(filename, self.clientName, 'add')

    def on_deleted(self, event):
        # event.is_directory is correct
        self.catch_all(event, 'DEL')
        filename = self.parse_filename(event.src_path)
        main.update_db(filename, self.clientName, 'del')

    def on_modified(self, event):
        # Note: event.is_directory is True for both files and folders
        # print self.ignore_pattern in event.src_path
        if not self.ignore_pattern in event.src_path:
            if event.is_directory:
                # For Mac OS X: FSEvents returns only the directory for file modified events,
                # which means event.is_directory is not reflecting the truth in Mac OS.
                # The following code detects the full path in Mac OS.
                files_in_dir = [event.src_path+"/"+f for f in os.listdir(event.src_path)]
                op_file_path = max(files_in_dir, key=os.path.getmtime)
                print ("MOD", op_file_path)
                filename = self.parse_filename(op_file_path)
                main.clientUpload(filename, self.clientName)

if __name__ == "__main__":

    # Format console logs
    logging.basicConfig( level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    # Start watchdog
    observer = Observer()
    event_handler = MyEventHandler('chun','http://172.25.179.70:8080/')
    observer.schedule(event_handler, path=UPLOAD_FOLDER, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
