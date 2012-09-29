"""Default r/a/dio theme"""

import os
import os.path
import itertools
try:
    from radio_project.theming.models import Types, Files
except:
    from theming.models import Types, Files

files= []
location = os.path.dirname(__file__)

temp_type = Types.get(name="template", type='te')
js_type = Types.get(name="js", type='st', directory="js")
css_type = Types.get(name="css", type='st',directory="css")
img_type = Types.get(name="image", type='st',directory="img")

def include_directory(name, type, filter=lambda x: True):
    for root, directories, filenames in os.walk(os.path.join(location, name), followlinks=True):
        for filename in filenames:
            if filter(filename):
                yield (os.path.join(root, filename).replace(location, '', 1), type)

for tup in include_directory("", type=temp_type,
                             filter=lambda x: x.endswith(".html")):
    files.append(tup)

# CSS files
for tup in include_directory("css", type=css_type):
    files.append(tup)

# Javascript files
for tup in include_directory("js", type=js_type):
    files.append(tup)

# Image files
for tup in include_directory("img", type=img_type):
    files.append(tup)