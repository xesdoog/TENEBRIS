import json
import logging
import logging.handlers
import os
import platform
import psutil
import sys
from hashlib import sha256
from pyinjector import inject, PyInjectorError

def executable_path():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def get_file_checksum(file):
    if os.path.exists(file):
        checksum = sha256()
        with open(file, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                checksum.update(block)

        return checksum.hexdigest()

def get_file_name(path) -> str:
    checksum  = str(get_file_checksum(path))[:8]
    file_name = f"{os.path.basename(path)} [{checksum}]"

    return file_name

def is_file_saved(name, list):
    if len(list) > 0:
        for file in list:
            if file["name"] == name:
                return True
    return False

def read_cfg(file):
    if os.path.isfile(file):
        with open(file, 'r') as f:
            return json.load(f)
    else:
        return []

def save_cfg(file, list):
    open_mode = os.path.exists(file) and 'w' or 'x'
    with open(file, open_mode) as f:
        json.dump(list, f, indent=2)

def update_process_list():
    proclist, procnames = [], []
    for p in psutil.process_iter(["name", "exe", "cmdline"]):
        procname = f"{p.info["name"]} [{p.pid}]"
        proclist.append({"name": procname, "pid": p.pid})
        procnames.append(procname)

    return proclist, procnames

class LOGGER:
    def __init__(self):
        self.logger = logging.getLogger("Main")
        log_handler = logging.handlers.RotatingFileHandler('./tenebris.log',
                                                maxBytes = 524288, # 0.5MB max file size
                                                backupCount = 2
                                                )
        logging.basicConfig(encoding = 'utf-8',
                        level    = logging.INFO,
                        format   = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
                        datefmt  = '%H:%M:%S',
                        handlers = [log_handler]
                    )

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)

    def OnStart(self, parent_path):
        LOCAL_VERSION = "v1.0.0"
        userOS        = platform.system()
        userOSarch    = platform.architecture()
        userOSrel     = platform.release()
        userOSver     = platform.version()
        workDir       = parent_path
        exeDir        = executable_path() + '\\'
        logfile = open("./tenebris.log", "a")
        logfile.write("--- Initializing TENEBRIS... ---\n\n")
        logfile.write(f"    ¤ Version: {LOCAL_VERSION}\n")
        logfile.write(f"    ¤ Operating System: {userOS} {userOSrel} x{userOSarch[0][:2]} v{userOSver}\n")
        logfile.write(f"    ¤ Working Directory: {workDir}\n")
        logfile.write(f"    ¤ Executable Directory: {exeDir}\n\n\n")
        logfile.flush()
        logfile.close()

def inject_dll(process, file, logger):
    try:
        return inject(process, file, uninject=False)
    except PyInjectorError as err:
        logger.info(f"Failed to inject module. Traceback: {err}")
        return 0
