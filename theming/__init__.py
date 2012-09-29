import os.path

STATIC_LOCAL = os.path.join(os.path.dirname(__file__), "static")
TEMPLATES_LOCAL = os.path.join(os.path.dirname(__file__), "templates")

__all__ = ["STATIC_LOCAL", "TEMPLATES_LOCAL"]