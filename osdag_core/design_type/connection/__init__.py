"""Connection registry.

This module exposes a mapping from user facing connection names to
their corresponding classes.  GUI elements can query this registry to
instantiate the correct connection object for a design.
"""

from .fin_plate_connection import FinPlateConnection

CONNECTION_REGISTRY = {
    "Fin-Plate": FinPlateConnection,
}

__all__ = ["CONNECTION_REGISTRY", "FinPlateConnection"]

