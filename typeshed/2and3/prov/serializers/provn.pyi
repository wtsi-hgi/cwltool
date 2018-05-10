# Stubs for prov.serializers.provn (Python 3.5)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from prov.serializers import Serializer
from typing import Any

__email__: str
logger: Any

class ProvNSerializer(Serializer):
    def serialize(self, stream, **kwargs): ...
    def deserialize(self, stream, **kwargs): ...
