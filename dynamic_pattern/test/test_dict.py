from DynamicPatternTOP import DynamicPatternTOP
my_class = DynamicPatternTOP()
circle_data = {"1": {"shape": "circle", "radius": 50, "color": (255, 0, 0), "position": (550, 0)},
               "2": {"shape": "circle", "radius": 50, "color": (255, 128, 0), "position": (550, 0)},
               "3": {"shape": "circle", "radius": 50, "color": (255, 255, 0), "position": (550, 0)},
               "4": {"shape": "circle", "radius": 50, "color": (0, 255, 0), "position": (550, 0)},
               "5": {"shape": "circle", "radius": 50, "color": (0, 0, 255), "position": (550, 0)},
               "6": {"shape": "circle", "radius": 50, "color": (0, 255, 255), "position": (550, 0)},
               "7": {"shape": "circle", "radius": 50, "color": (255, 0, 255), "position": (550, 0)},
               "8": {"shape": "circle", "radius": 50, "color": (0, 0, 0), "position": (550, 0)},
               "cross_line": "False"
               }
test = DynamicPatternTOP()
test.set_pattern_dict(circle_data)
test.set_resolution()
test.save_image()
test.save_json()
test.show()