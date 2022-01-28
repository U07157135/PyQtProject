import base64
import ctypes
import time
import logging
from ctypes import c_ulong, wintypes

import cv2
import numpy as np


class DisplayPattern:
    def __init__(self):
        t = time.localtime()

        log_name = "log/" + \
            str(t.tm_year) + "-" + \
            str(t.tm_mon) + "-" +\
            str(t.tm_mday) + "-" + \
            str(t.tm_hour) + "-" +\
            str(t.tm_min) + "-" +\
            str(t.tm_sec) + ".log"

        log_format="<TIME>%(asctime)s <LINE>%(lineno)d %(funcName)s <%(levelname)s> %(message)s"

        logging.basicConfig(format=log_format,filename=log_name, filemode='w', level=logging.DEBUG)

        self.dis_num_dic = {}
        self.monitor_handle_position_dic = {}
        self.is_brightness_stop_change_flag = {
            "top": True, "n": True, "w": True, "s": True, "e": True}
        self.brightness_change_delay_time = {}
        self.last_change_brightness_time = {}

        self.dxva2 = ctypes.windll.Dxva2

        import win32api

        monitor_list = win32api.EnumDisplayMonitors()

        for current_monitor in monitor_list:

            monitor_info = win32api.GetMonitorInfo(current_monitor[0])

            display_num = monitor_info["Device"].lstrip("\\.\\")
            monitor_handle_value = current_monitor[0].handle
            monitro_left_top_x = monitor_info["Monitor"][0]
            monitro_left_top_y = monitor_info["Monitor"][1]

            self.monitor_handle_position_dic[display_num] = [
                monitor_handle_value,
                (monitro_left_top_x, monitro_left_top_y),
            ]

    def show_display_number(self):

        try:
            for monitor_handle_position_dic in self.monitor_handle_position_dic:
                x, y = self.monitor_handle_position_dic[monitor_handle_position_dic][1]
                img_white_bg = np.zeros((1920, 1920, 3), np.uint8)
                img_white_bg[:] = (255, 255, 255)
                text = monitor_handle_position_dic
                cv2.putText(
                    img_white_bg,
                    text,
                    (495, 1020),
                    cv2.FONT_HERSHEY_TRIPLEX,
                    6,
                    (0, 0, 0),
                    8,
                    cv2.LINE_AA,
                )
                cv2.namedWindow(text, cv2.WINDOW_NORMAL)
                cv2.setWindowProperty(
                    text, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.moveWindow(text, x, y)
                cv2.imshow(text, img_white_bg)
            cv2.waitKey(1)
            logging.info("OK")
            return True

        except Exception as ex:
            logging.error(str(ex))
            return False

    def set_direction(
        self,
        dis_num_top: str,
        dis_num_n: str,
        dis_num_w: str,
        dis_num_s: str,
        dis_num_e: str,
    ):

        try:
            dis_num_top = dis_num_top.upper()
            dis_num_n = dis_num_n.upper()
            dis_num_w = dis_num_w.upper()
            dis_num_s = dis_num_s.upper()
            dis_num_e = dis_num_e.upper()

            if dis_num_top[:7] == "DISPLAY":
                self.dis_num_dic["top"] = dis_num_top
            else:
                return False, ('top', dis_num_top)

            if dis_num_n[:7] == "DISPLAY":
                self.dis_num_dic["n"] = dis_num_n
            else:
                return False, ('n', dis_num_n)

            if dis_num_w[:7] == "DISPLAY":
                self.dis_num_dic["w"] = dis_num_w
            else:
                return False, ('w', dis_num_w)

            if dis_num_s[:7] == "DISPLAY":
                self.dis_num_dic["s"] = dis_num_s
            else:
                return False, ('s', dis_num_s)

            if dis_num_e[:7] == "DISPLAY":
                self.dis_num_dic["e"] = dis_num_e
            else:
                return False, ('e', dis_num_e)

            logging.info("OK")
            return True

        except Exception as ex:
            logging.error(str(ex))
            return False

    def get_brightness(self, direction: str):

        try:
            display_num = self.dis_num_dic[direction]
            monitor_handle = self.monitor_handle_position_dic[display_num][0]

            # Specify physical mointor
            physical_monitor = (PHYSICAL_MONITOR * 1)()
            self.dxva2.GetPhysicalMonitorsFromHMONITOR(
                monitor_handle, c_ulong(1), physical_monitor
            )

            # Get Minimum/Current/Maximum of brightness
            min_brightness = wintypes.DWORD()
            max_brightness = wintypes.DWORD()
            current_brightness = wintypes.DWORD()
            self.dxva2.GetMonitorBrightness(
                physical_monitor[0].hPhysicalMonitor,
                ctypes.byref(min_brightness),
                ctypes.byref(current_brightness),
                ctypes.byref(max_brightness),
            )
            logging.info("OK")
            return True, current_brightness.value

        except Exception as ex:
            logging.error(str(ex))
            return False, str(ex)

    def set_brightness(self, direction: str, target_brightness: int):

        try:
            if not self.is_brightness_stop_change_flag[direction]:

                sotp_change_brightness_time = (
                    self.brightness_change_delay_time[direction] +
                    self.last_change_brightness_time[direction]
                )

                if time.time() >= sotp_change_brightness_time:
                    self.is_brightness_stop_change_flag[direction] = True

                else:

                    brightness_change_time_left = sotp_change_brightness_time - time.time()
                    logging.info("Brightness still change: " + str(round(brightness_change_time_left, 2)))
                    return False, round(brightness_change_time_left, 2)

            if self.is_brightness_stop_change_flag[direction]:
                currnet_brightness = self.get_brightness(direction)[1]
                brightness_difference = abs(
                    currnet_brightness - target_brightness)

                self.brightness_change_delay_time[direction] = brightness_difference / 3.33
                display_num = self.dis_num_dic[direction]
                monitor_handle = self.monitor_handle_position_dic[display_num][0]

                # Specify physical mointor
                physical_monitor = (PHYSICAL_MONITOR * 1)()
                self.dxva2.GetPhysicalMonitorsFromHMONITOR(
                    monitor_handle, c_ulong(1), physical_monitor
                )

                # Modify brightness
                self.dxva2.SetMonitorBrightness(
                    physical_monitor[0].hPhysicalMonitor, target_brightness
                )

                if brightness_difference > 0:
                    self.is_brightness_stop_change_flag[direction] = False
                    self.last_change_brightness_time[direction] = time.time()
                logging.info("OK")
                return True, round(self.brightness_change_delay_time[direction], 2)

        except Exception as ex:
            logging.error(str(ex))
            return False, str(ex)

    def set_all_brightness(self, target_brightness: int):
        try:

            is_assert, err_msg = self.set_brightness('top', target_brightness)
            err_msg = ('top', err_msg)
            assert is_assert

            is_assert, err_msg = self.set_brightness('n', target_brightness)
            err_msg = ('n', err_msg)
            assert is_assert

            is_assert, err_msg = self.set_brightness('w', target_brightness)
            err_msg = ('w', err_msg)
            assert is_assert

            is_assert, err_msg = self.set_brightness('s', target_brightness)
            err_msg = ('s', err_msg)
            assert is_assert

            is_assert, err_msg = self.set_brightness('e', target_brightness)
            err_msg = ('e', err_msg)
            assert is_assert
            logging.info("OK")
            return True

        except Exception as ex:
            logging.error(str(ex))
            logging.error(err_msg)
            return False

    def set_img(self, direction: str, img_base64: str):

        try:
            if True:
                display_num = self.dis_num_dic[direction]
                x, y = self.monitor_handle_position_dic[display_num][1]

                img_base64_decode = base64.b64decode(img_base64)
                img_np_ndarray = np.frombuffer(img_base64_decode, dtype=np.uint8)
                img_source = cv2.imdecode(img_np_ndarray, 1)

                # Set Window Title
                cv2.namedWindow(direction, cv2.WINDOW_NORMAL)

                # Set Window Property - FULLSCREEN
                cv2.setWindowProperty(direction, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

                # Move Window - Position(x, y)
                cv2.moveWindow(direction, x, y)

                # Show Image Window
                cv2.imshow(direction, img_source)
            cv2.waitKey(1000)
            logging.info("OK")
            return True

        except Exception as ex:
            logging.error(str(ex))
            return False

    def set_brightness_img(self, direction: str, target_brightness: int, img_base64: str):

        try:
            is_assert = self.set_img(direction, img_base64)
            assert is_assert
            is_assert, err_msg = self.set_brightness(
                direction, target_brightness)
            assert is_assert
            logging.info("OK")
            return True, err_msg

        except Exception as ex:
            logging.error(str(ex))
            return False, str(ex)

    def close_all_window(self):

        try:
            cv2.destroyAllWindows()
            logging.info("OK")
            return True

        except Exception as ex:
            logging.error(str(ex))
            return False

    def close_window(self, direction: str):

        try:
            cv2.destroyWindow(direction)
            logging.info("OK")
            return True

        except Exception as ex:
            logging.error(str(ex))
            return False


class PHYSICAL_MONITOR(ctypes.Structure):
    _fields_ = [
        ("hPhysicalMonitor", wintypes.HANDLE),
        (
            "szPhysicalMonitorDescription",
            ctypes.c_wchar * 128,
        ),
    ]


if __name__ == "__main__":
    dp = DisplayPattern()

    import base64

    with open("pattern_top.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    msg = dp.set_direction("DISPLAY4", "DISPLAY5",
                           "DISPLAY6", "DISPLAY1", "DISPLAY2")
    print(msg)
    # print(dp.dis_num_dic)
    msg = dp.get_brightness("top")
    print(msg)
    dp.set_img("top", encoded_string)
    time.sleep(5)

    dp.close_window("top")
