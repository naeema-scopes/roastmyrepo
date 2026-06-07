"""Module with dead code for testing."""

import os
import json
import sys

used_var = "I am used"
unused_var = "I am never used"
__all__ = ["used_var"]
_ = "throwaway"
_private = "private var"

print(used_var)
print(os.getcwd())
