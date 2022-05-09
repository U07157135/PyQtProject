from DynamicPatternTOP import DynamicPatternTOP
my_class = DynamicPatternTOP()
my_class.set_resolution(1920, 1080)
my_class.load_json('json\\test1.json')
my_class.save_image()
my_class.show()
