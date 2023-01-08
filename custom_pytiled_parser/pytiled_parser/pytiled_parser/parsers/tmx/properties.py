import xml.etree.ElementTree as etree
from pathlib import Path

from pytiled_parser.properties import Properties, Property
from pytiled_parser.util import parse_color
import pytiled_parser

# ---- Changed ----
class ObjectID:
    tilemap = None
    def __init__(self, object_id):
        self.id = object_id

    def get_object(self):
        if self.tilemap is None:
            raise Exception("tilemap have not been specified yet.")
        else:
            return _get_object_by_id(self.tilemap, self.id)
# ---- Changed End ----

def parse(raw_properties: etree.Element) -> Properties:

    final: Properties = {}
    value: Property

    for raw_property in raw_properties.findall("property"):

        type_ = raw_property.attrib.get("type")

        if "value" not in raw_property.attrib:
            continue

        value_ = raw_property.attrib["value"]

        if type_ == "file":
            value = Path(value_)
        elif type_ == "color":
            value = parse_color(value_)
        elif type_ == "int" or type_ == "float":
            value = float(value_)
        elif type_ == "bool":
            if value_ == "true":
                value = True
            else:
                value = False
        # ---- Changed ----
        elif type_ == "object":
            value = ObjectID(float(value_))
        # ---- Changed End ----
        else:
            value = value_
        final[raw_property.attrib["name"]] = value

    return final

# ---- Changed ----
def _get_object_by_id(tilemap, tile_id):
    for layer in tilemap.layers:
        if isinstance(layer, pytiled_parser.ObjectLayer):
            for cur_object in layer.tiled_objects:
                if cur_object.id == tile_id:
                    return cur_object
    return None
# ---- Changed End ----
