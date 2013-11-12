from os.path import expanduser
import os
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

# Configs
home = expanduser("~")
UPLOAD_FOLDER = home + '/uploads'  # assume client user has a dir called uploads under home dir
SERVER_URL = 'http://localhost:5000'


class MyEventHandler(PatternMatchingEventHandler):
    """ customized file system event handler
    """
    ignore_pattern = ".DS_Store"

    def catch_all(self, event, op):
        if not self.ignore_pattern in event.src_path:
            print (op, event.is_directory, event.src_path)

    def parse_filename(self,file_path):
        temp = file_path.split("uploads/")
        return temp[1]

    def download(self, filename):
        print "Syncing ..."
        os.system("curl http://127.0.0.1:5000/uploads/hi.txt > ~/uploads/hi2.txt | ~/Desktop")
        #download = "curl http://127.0.0.1:5000/uploads/"+filename + " > " + UPLOAD_FOLDER+"/"+filename
        #os.system(download)

    def delete(self, filename):
        # delete file on client machine
        return

    def on_created(self, event):
        # event.is_directory is correct
        self.catch_all(event, 'NEW')
        filename = self.parse_filename(event.src_path)
        self.download(filename)

    def on_deleted(self, event):
        # event.is_directory is correct
        self.catch_all(event, 'DEL')

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
                filename = self.parse_filename(event.src_path)
                self.download(filename)

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
