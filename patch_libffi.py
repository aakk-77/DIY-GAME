"""Patch python-for-android libffi recipe to fix LT_SYS_SYMBOL_USCORE issue."""
import sys
import os

try:
    import pythonforandroid
    p4a_path = pythonforandroid.__path__[0]
except ImportError:
    print("ERROR: python-for-android not installed")
    sys.exit(1)

recipe_path = os.path.join(p4a_path, "recipes", "libffi", "__init__.py")
print(f"Patching: {recipe_path}")

with open(recipe_path, "r") as f:
    content = f.read()

# Find the autogen.sh call and add Python patch code before it
old = "            shprint(sh.Command('./autogen.sh'), _env=env)"

if old not in content:
    print("ERROR: Could not find autogen.sh call")
    print("=== RECIPE (first 2000 chars) ===")
    print(content[:2000])
    sys.exit(1)

patch = '''            # Patch configure.ac to define LT_SYS_SYMBOL_USCORE
            # (removed from modern libtool, needed by libffi's configure.ac)
            import re as _re
            _cfg = os.path.join(self.get_build_dir(arch.arch), 'configure.ac')
            if os.path.exists(_cfg):
                with open(_cfg, 'r') as _f:
                    _c = _f.read()
                if 'LT_SYS_SYMBOL_USCORE' in _c and 'AC_DEFUN([LT_SYS_SYMBOL_USCORE]' not in _c:
                    _c = 'AC_DEFUN([LT_SYS_SYMBOL_USCORE], [])\\n' + _c
                    with open(_cfg, 'w') as _f:
                        _f.write(_c)
                    print(f'Patched: {_cfg}')
            shprint(sh.Command('./autogen.sh'), _env=env)
'''

new_content = content.replace(old, patch)

with open(recipe_path, "w") as f:
    f.write(new_content)

print("Successfully patched libffi recipe!")
