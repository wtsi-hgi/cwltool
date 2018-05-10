# Stubs for networkx.algorithms.connectivity.edge_augmentation (Python 3.5)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from collections import namedtuple
from typing import Any, Optional

def is_k_edge_connected(G, k): ...
def is_locally_k_edge_connected(G, s, t, k): ...
def k_edge_augmentation(G, k, avail: Optional[Any] = ..., weight: Optional[Any] = ..., partial: bool = ...): ...

MetaEdge = namedtuple('MetaEdge', <ERROR>)
