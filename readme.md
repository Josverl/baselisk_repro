
Minimal repro for a Basilisk divergence from pyright/mypy.
`asyncio/__init__.pyi` in micropython-stdlib-stubs re-exports its public API
from submodules (`from .tasks import *`, `from .tasks import Task as Task`,
`from .runners import *`, ...).
pyright and mypy follow these package re-exports, so `asyncio.sleep`,
`asyncio.Task` and `asyncio.run` all resolve.
Basilisk v0.34.0 (with `typeshed-path` pointing at the stub tree) resolves the
submodules directly (`from asyncio.tasks import sleep` works) but does NOT
surface names re-exported through the package `__init__.pyi` as attributes of
the package, reporting `imports_module_attribute`:
    Module `asyncio` has no attribute `sleep`
    Module `asyncio` has no attribute `Task`
    Module `asyncio` has no attribute `run`
See https://github.com/Nimblesite/Basilisk (issues #271 / PRs #277, #292 added
the working `typeshed-path` feature; this re-export propagation is a follow-up).


pip install micropython-stdlib-stubs --target typings --no-user

```
basilisk check reexport.py
jos@SB26:~/bslx_repro$ basilisk check ./reexport.py
error[imports_module_attribute]: Module `asyncio` has no attribute `sleep`
  --> ./reexport.py:3:10
  |
3 | asleep = asyncio.sleep  # re-exported via `from .tasks import *`
  |          ^^^^^^^^^^^^^
  |
   = help: declare `sleep` in the local stub `/home/jos/bslx_repro/typings/stdlib/asyncio/__init__.pyi`, or fix the typo. To allow any attribute, keep `def __getattr__(name: str) -> Any: ...` in the stub.
   = note: A local stub is authoritative — Basilisk only sees the names it declares. https://typing.python.org/en/latest/guides/writing_stubs.html
   = see: https://www.basilisk-python.dev/errors/imports_module_attribute

error[imports_module_attribute]: Module `asyncio` has no attribute `Task`
  --> ./reexport.py:4:9
  |
4 | atask = asyncio.Task  # re-exported via explicit `from .tasks import Task as Task`
  |         ^^^^^^^^^^^^
  |
   = help: declare `Task` in the local stub `/home/jos/bslx_repro/typings/stdlib/asyncio/__init__.pyi`, or fix the typo. To allow any attribute, keep `def __getattr__(name: str) -> Any: ...` in the stub.
   = note: A local stub is authoritative — Basilisk only sees the names it declares. https://typing.python.org/en/latest/guides/writing_stubs.html
   = see: https://www.basilisk-python.dev/errors/imports_module_attribute

error[imports_module_attribute]: Module `asyncio` has no attribute `run`
  --> ./reexport.py:5:8
  |
5 | arun = asyncio.run  # re-exported via `from .runners import *`
  |        ^^^^^^^^^^^
  |
   = help: declare `run` in the local stub `/home/jos/bslx_repro/typings/stdlib/asyncio/__init__.pyi`, or fix the typo. To allow any attribute, keep `def __getattr__(name: str) -> Any: ...` in the stub.
   = note: A local stub is authoritative — Basilisk only sees the names it declares. https://typing.python.org/en/latest/guides/writing_stubs.html
   = see: https://www.basilisk-python.dev/errors/imports_module_attribute

Found 3 diagnostics (3 errors).

```

```
:~/bslx_repro$ mypy reexport.py 
Success: no issues found in 1 source file

:~/bslx_repro$ pyright reexport.py 
0 errors, 0 warnings, 0 informations
```