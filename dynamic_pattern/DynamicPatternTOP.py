import cv2
import json
import os
import numpy as np


class DynamicPatternTOP():
    def __init__(self):
        self.pettern_dict = {}
        self.is_cross_line = False

    def set_pattern_dict(self, dict):
        self.pettern_dict = dict
        return self.pettern_dict

    def load_json(self, path=''):
        load_json_path = path
        with open(load_json_path, 'r') as f:
            self.pettern_dict = json.loads(f.read())
        return self.pettern_dict

    def set_resolution(self, length=1920, width=1080):
        self.res_length = length
        self.res_width = width
        self.center_length = self.res_length//2
        self.center_width = self.res_width//2

    def save_image(self, path=''):
        radius_sum = 0
        save_image_path = path
        self.background = np.ones(
            (self.res_width, self.res_length, 3), dtype="uint8")
        self.background *= 255
        for circle_index in self.pettern_dict.keys():
            if circle_index != "cross_line":
                radius_sum += self.pettern_dict[circle_index]["radius"]
        for i in self.pettern_dict.keys():
            if i != "cross_line":
                circle_index = str(len(self.pettern_dict) - int(i))
                radius = self.pettern_dict[circle_index]["radius"]
                color_RGB = list(self.pettern_dict[circle_index]["color"])
                color_RGB.reverse()
                if "position" not in self.pettern_dict[circle_index]:
                    position_x = 0
                    position_y = 0
                else:
                    position = self.pettern_dict[circle_index]["position"]
                    position_x = position[0]
                    position_y = position[1]
                if self.pettern_dict[circle_index]["shape"] == "circle":
                    cv2.circle(self.background,
                               center=(self.center_length+position_x,
                                       self.center_width+position_y),
                               radius=radius_sum,
                               color=color_RGB,
                               thickness=-1)
                if self.pettern_dict[circle_index]["shape"] == "square":
                    p1 = (self.center_length-radius_sum+position_x,
                          self.center_width-radius_sum+position_y)
                    p2 = (self.center_length+radius_sum+position_x,
                          self.center_width+radius_sum+position_y)
                    cv2.rectangle(self.background,
                                  p1,
                                  p2,
                                  color=color_RGB,
                                  thickness=-1)
                radius_sum -= radius
            else:
                if self.pettern_dict["cross_line"] == "True":
                    cv2.line(self.background, (0, self.center_width),
                             (self.res_length, self.center_width), (0, 0, 0), 2)
                    cv2.line(self.background, (self.center_length, 0),
                             (self.center_length, self.res_length), (0, 0, 0), 2)
        cv2.imwrite(os.path.join(save_image_path, "circle.png"),
                    self.background, [cv2.IMWRITE_PNG_COMPRESSION, 9])

    def save_json(self, path='', name="image.json"):
        json_file_name = name
        save_json_path = path
        with open(os.path.join(save_json_path, json_file_name), 'w') as savefile:
            savefile.write(json.dumps(self.pettern_dict, indent=4))

    def show(self):
        cv2.namedWindow("circle", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(
            "circle", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("circle", self.background)
        # cv2.moveWindow("circle", 1920, 0)
        cv2.waitKey(0)
        cv2.destroyWindow("circle")
