import sys
import subprocess
import re

try:
    import configparser
except:
    import ConfigParser as configparser


class ConfController:
    """This class exposes information about pen/tablet pointing device configuration
    and gives methods for reconfiguring those devices"""

    pen_touch_ids = None
    monitor_ids = None
    display = None

    def __init__(self):
        self.pen_touch_ids = self.get_pen_touch_ids()
        self.monitor_ids, self.display = self.get_monitor_ids()

    def refresh(self):
        self.refreshMonitorIds()
        self.refreshPenTouchIds()

    def refreshMonitorIds(self):
        """reload monitor layout information """
        self.monitor_ids, self.display = self.get_monitor_ids()

    def refreshPenTouchIds(self):
        """reload pen/touch tabled ids"""
        self.pen_touch_ids = self.get_pen_touch_ids()

    def getPointerDeviceMode(self, id):
        """Queries the pointer device mode. Returns "asolute" or "relative" """
        retval = subprocess.Popen(
            "xinput query-state %d" % (id), shell=True, stdout=subprocess.PIPE
        ).stdout.read()

        for line in retval.split(b"\n"):
            if b"mode=" in line.lower():
                return line.lower().split(b"mode=")[1].split(b" ")[0]
        return None

    def get_pen_touch_ids(self):
        """Returns a list of input id/name pairs for all available pen/tablet xinput devices"""
        retval = subprocess.Popen(
            "xinput list", shell=True, stdout=subprocess.PIPE
        ).stdout.read()

        ids = {}
        for line in retval.split(b"]"):
            if b"pointer" in line.lower() and b"master" not in line.lower():
                id = int(line.split(b"id=")[1].split(b"[")[0].strip())
                name = line.split(b"id=")[0].split(b"\xb3", 1)[1].strip()
                if self.getPointerDeviceMode(id) == b"absolute":
                    key = name + b"(%d)" % id
                    ids[key.decode() if isinstance(key, bytes) else key] = {"id": id}
        return ids

    def get_monitor_ids(self):
        """Returns a list of screens composing the default x-display"""
        retval = subprocess.Popen(
            "xrandr", shell=True, stdout=subprocess.PIPE
        ).stdout.read()

        display0_dim = {"w": None, "h": None}
        monitors = {}
        for line in retval.split(b"\n"):
            if b"Screen 0" == line[:8]:
                # here the xrandr dev meant to call it display 0 in line with xorg.
                for part in line.split(b", "):
                    if b"current" in part:
                        display0_dim["w"] = int(
                            part.split(b"current")[1].split(b"x")[0]
                        )
                        display0_dim["h"] = int(
                            part.split(b"current")[1].split(b"x")[1]
                        )
            elif b"connected" in line and b"disconnected" not in line:
                port = line.split(b" ")[0]
                layout_strings = line.split(b"(")[0].strip().split(b" ")
                for element in layout_strings:
                    if (
                        re.match(br"^[0-9]+x[0-9]+\+[0-9]+\+[0-9]+$", element.strip())
                        is not None
                    ):
                        placement = element
                if layout_strings[-1].strip().lower() in ("right", "left", "inverted"):
                    rotation = layout_strings[-1].strip().lower()
                else:
                    rotation = None
                w = int(placement.split(b"x")[0])
                h = int(placement.split(b"x")[1].split(b"+")[0])
                x = int(placement.split(b"x")[1].split(b"+")[1])
                y = int(placement.split(b"x")[1].split(b"+")[2])
                mon_name = port
                monitors[
                    mon_name.decode() if isinstance(mon_name, bytes) else mon_name
                ] = {"w": w, "h": h, "x": x, "y": y, "rotation": rotation}
        # add display to monitors
        monitors["display"] = {
            "w": display0_dim["w"],
            "h": display0_dim["h"],
            "x": 0,
            "y": 0,
            "rotation": None,
        }

        return monitors, display0_dim

    def get_device_ctm(self, id):
        command = subprocess.Popen(
            'xinput list-props %d | grep "Coordinate Transformation Matrix"' % id,
            shell=True,
            stdout=subprocess.PIPE,
        ).stdout.read()
        return command

    def set_device_ctm(self, id, ctm="0.5 0 0.5 0 1 0 0 0 1"):
        command = subprocess.Popen(
            "xinput set-prop %d 'Coordinate Transformation Matrix' %s" % (id, ctm),
            shell=True,
            stdout=subprocess.PIPE,
        ).stdout.read()
        return command

    def reset_device_ctm(self, id):
        command = subprocess.Popen(
            "xinput set-prop %d 'Coordinate Transformation Matrix' 1 0 0 0 1 0 0 0 1"
            % id,
            shell=True,
            stdout=subprocess.PIPE,
        ).stdout.read()
        return command

    def set_device_axes_swap(self, id, swap=False):
        command = subprocess.Popen(
            "xinput set-prop %d --type=int 'Evdev Axes Swap' %d" % (id, int(swap)),
            shell=True,
            stdout=subprocess.PIPE,
        ).stdout.read()
        return command

    def set_device_axis_inversion(self, id, xinv=False, yinv=False):
        command = subprocess.Popen(
            "xinput set-prop %d --type=int 'Evdev Axis Inversion' %d %d"
            % (id, int(xinv), int(yinv)),
            shell=True,
            stdout=subprocess.PIPE,
        ).stdout.read()
        return command

    def set_map_to_output(self, id, monitor):
        command = subprocess.Popen(
            "xinput map-to-output %d %s" % (id, monitor),
            shell=True,
            stdout=subprocess.PIPE,
        ).stdout.read()
        return command

    def set_device_axis_rotation(self, id, rotation=None):
        if rotation == "right":
            swap = True
            xinv = False
            yinv = True
        elif rotation == "left":
            swap = True
            xinv = True
            yinv = False
        elif rotation == "inverted":
            swap = False
            xinv = True
            yinv = True
        else:
            swap = False
            xinv = False
            yinv = False
        self.set_device_axes_swap(id, swap)
        self.set_device_axis_inversion(id, xinv, yinv)

    def set_pen_to_monitor(self, pen, monitor):
        """Configure pen to control monitor"""
        penid = self.pen_touch_ids[pen]["id"]
        dw = self.display["w"]
        dh = self.display["h"]
        mw = self.monitor_ids[monitor]["w"]
        mh = self.monitor_ids[monitor]["h"]
        mx = self.monitor_ids[monitor]["x"]
        my = self.monitor_ids[monitor]["y"]
        rot = self.monitor_ids[monitor]["rotation"]
        ctm = generate_ctm(dw, dh, mw, mh, mx, my)
        # self.resetDeviceCTM(penid)
        self.set_device_ctm(penid, ctm)
        self.set_device_axis_rotation(penid, rot)
        # self.setMapToOutput(penid, monitor)


def generate_ctm(dw, dh, mw, mh, mx, my):
    """Generate coordinate transform matrix for a tablet controlling screen out of n_screens in a row"""
    return "%f 0 %f 0 %f %f 0 0 1" % (
        float(mw) / dw,
        float(mx) / dw,
        float(mh) / dh,
        float(my) / dh,
    )
