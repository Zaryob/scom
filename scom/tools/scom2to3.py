#!/usr/bin/python
# -*- coding: utf-8 -*-

import dbus
import glob
import os
import time

COMAR_DB_OLD = "/var/db/scom/code"
COMAR_DB_NEW = "/var/db/scom3/scripts"
COMAR_ADDRESS = "tr.org.sulin.scom.updated"
COMAR_IFACE = "tr.org.sulin.scom"
COMAR_TIMEOUT = 10

def main():
    if os.getuid() != 0:
        print("Must be run as root.")
        return -1

    # If COMAR 3.0 database is already initialized, do nothing.
    init = False
    ignore_scom = False
    if os.path.exists(COMAR_DB_NEW):
        for model in os.listdir(COMAR_DB_NEW):
            files = os.listdir(os.path.join(COMAR_DB_NEW, model))
            if "scom.py" in files:
                files.remove("scom.py")
                ignore_scom = True
            if len(files):
                init = True
                break
        if init:
            print("COMAR database is already initialized.")
            return 0

    bus = dbus.SystemBus()
    obj = None

    # Old PiSi releases start new COMAR service after all postInstall
    # operations complete. We start our own COMAR service so we 
    # guarantee that we register all scripts to new COMAR.
    os.system("/usr/sbin/scom -i -b %s &" % COMAR_ADDRESS)

    # Wait until service gets ready
    timeout = COMAR_TIMEOUT
    while timeout > 0:
        try:
            obj = bus.get_object(COMAR_ADDRESS, "/", introspect=False)
            break
        except dbus.exceptions.DBusException:
            pass
        time.sleep(0.2)
        timeout -= 0.2

    if not obj:
        print("Unable to start new COMAR service.")
        return -2

    # Register all scripts
    for filename in os.listdir(COMAR_DB_OLD):
        if filename.endswith(".py"):
            _group, _class, _app = filename.split("_", 2)
            _model = "%s.%s" % (_group, _class)
            _app = _app.rsplit(".py", 1)[0]
            # If COMAR package is already registered, pass
            if _app == "scom" and ignore_comar:
                continue
            obj.register(_app, _model, os.path.join(COMAR_DB_OLD, filename), dbus_interface=COMAR_IFACE)
            print("Registering %s" % filename)

    return 0

if __name__ == "__main__":
    main()
