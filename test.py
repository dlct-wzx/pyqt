from PIL.TiffTags import TAGS
from PIL import Image

with Image.open('Red.TIF') as img:
    meta_dict = {TAGS[key]: img.tag[key] for key in img.tag.keys()}
print(meta_dict)