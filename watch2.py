__author__ = 'Chris'

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
UPLOAD_FOLDER = home + 'Dropbox/server/log' # assume client user has a dir called uploads under home dir

class MyEventHandler(FileSystemEventHandler):
    """ customized file system event handler
    """

    def __init__(self, client_name, server_url, time):
        super(FileSystemEventHandler, self).__init__()
        self.clientName = client_name
        self.serverUrl = server_url
        self.ignore_pattern = ".DS_Store"
        self.time = time

    def catch_all(self, event, op):
        if not self.ignore_pattern in event.src_path:
            print (op, event.src_path)

    def parse_filename(self, file_path):
        temp = file_path.split("Dropbox/server/log")
        return temp[1]


    def on_modified(self, event):
        # Note: event.is_directory is True for both files and folders
        # print self.ignore_pattern in event.src_path
        if self.time == 0:
            self.time = os.stat(expanduser('~/Dropbox/server/log/sys_log.txt')).st_mtime
        else:
            if os.stat(expanduser('~/Dropbox/server/log/sys_log.txt')).st_mtime - self.time < 200:
                self.time = os.stat(expanduser('~/Dropbox/server/log/sys_log.txt')).st_mtime
                return
        main.clientDownload(self.clientName, self.serverUrl)


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
