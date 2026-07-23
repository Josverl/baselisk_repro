
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



### Change log:
- Updated `pyproject.toml` to include the `stubs` extra to allow pinning of the (dev) dependencies to the `micropython-stdlib-stubs` and `micropython-esp32-stubs` packages.
- Add tests used to verify correct type checing of the MicroPython stdlib stubs used for other typecheckers
  See : https://github.com/Josverl/micropython-stubs/tree/main/tests/quality_tests/feat_stdlib 


## uv based installation of the stubs

>   uv pip install -r pyproject.toml --extra stubs --target typings


## Remaining errors

It appears that basilisk does not allow a non-stdlib stub to re-export symbols from a stdlib stuv.

This surfaces in the `uio` module, which re-exports `StringIO` and `BytesIO` from the `io` module. Basilisk does not see these symbols as attributes of the `uio` module, and reports them as missing.

While this is a specific issue with the `uio` module, it similarly affectsother modules that re-export symbols from the stdlib.
I think that this is not exclusive to MicroPython, but is a general issue with Basilisk's handling of re-exports.

basilisk check src

```
jos@SB26:~/bslx_repro$ basilisk check  src
2026-07-22T23:58:51.832017Z  WARN basilisk::pipeline::typeshed: typeshed source status active_source="custom" commit_identity="not supplied" tree_identity="not supplied" license_status=NotSupplied license_reference="not supplied"
2026-07-22T23:58:51.832096Z  WARN basilisk::pipeline::typeshed: typeshed source warning warning_code="UNPINNED" warning_message="UNPINNED — folder contents can change; version or content-address the folder externally"
2026-07-22T23:58:51.832103Z  WARN basilisk::pipeline::typeshed: typeshed source warning warning_code="USER-MANAGED SOURCE" warning_message="USER-MANAGED SOURCE — license and contents supplied by user"
error[imports_module_attribute]: Module `uio` has no attribute `StringIO`
  --> src/check_uio.py:7:12
  |
7 | buffer_1 = uio.StringIO(alloc_size) 
  |            ^^^^^^^^^^^^
  |
   = help: declare `StringIO` in the local stub `/home/jos/bslx_repro/typings/uio.pyi`, or fix the typo. To allow any attribute, keep `def __getattr__(name: str) -> Any: ...` in the stub.
   = note: A local stub is authoritative — Basilisk only sees the names it declares. https://typing.python.org/en/latest/guides/writing_stubs.html
   = see: https://www.basilisk-python.dev/errors/imports_module_attribute

error[imports_module_attribute]: Module `uio` has no attribute `BytesIO`
  --> src/check_uio.py:8:12
  |
8 | buffer_2 = uio.BytesIO(alloc_size) 
  |            ^^^^^^^^^^^
  |
   = help: declare `BytesIO` in the local stub `/home/jos/bslx_repro/typings/uio.pyi`, or fix the typo. To allow any attribute, keep `def __getattr__(name: str) -> Any: ...` in the stub.
   = note: A local stub is authoritative — Basilisk only sees the names it declares. https://typing.python.org/en/latest/guides/writing_stubs.html
   = see: https://www.basilisk-python.dev/errors/imports_module_attribute

Found 2 diagnostics (2 errors).
```

compare pyright && mypy

``` 
jos@SB26:~/bslx_repro$ pyright -p .
/home/jos/bslx_repro/src/check_collections/check_namedtuple_2.py
  /home/jos/bslx_repro/src/check_collections/check_namedtuple_2.py:7:13 - information: Type of "WifiConfig" is "type[WifiConfig]"
/home/jos/bslx_repro/src/check_json/check_json.py
  /home/jos/bslx_repro/src/check_json/check_json.py:39:17 - information: Type of "seps_1" is "tuple[Literal[','], Literal[':']]"
/home/jos/bslx_repro/src/check_os/check_uname.py
  /home/jos/bslx_repro/src/check_os/check_uname.py:17:13 - information: Type of "os_uname" is "uname_result"
0 errors, 0 warnings, 3 informations

jos@SB26:~/bslx_repro$ mypy src
src/check_os/check_uname.py:17: note: Revealed type is "tuple[str, str, str, str, str, fallback=_mpy_shed.uname_result]"
src/check_json/check_json.py:39: note: Revealed type is "tuple[str, str]"
src/check_collections/check_namedtuple_2.py:7: note: Revealed type is "def (ssid: Any, password: Any) -> tuple[Any, Any, fallback=check_namedtuple_2.WifiConfig]"
Success: no issues found in 24 source files

``` 

**Background Information:**
> The `u`-prefix is allowed in Micropython v1.x to force an import of a built-in module. For example, import utime instead of import time. For example, time.py on the filesystem could look like:

    from utime import *

    def extra_method():
    pass

> This way is still supported, but the sys.path method described above is now preferred as the u-prefix will be removed from the names of built-in modules in a future version of MicroPython. ( v2.x )

If basilisk cannot handle this, I probably can work around this by co-locating the u<modules> with the stdlib stubs. This is a bit of a hack and will require rework in the stub packages, that it is not needed for any other type checker, but it works in a simple test.

``` bash
# satisfy basilisk by co-locating the u<modules> with the stdlib stubs
mv typings/uio.pyi typings/stdlib/uio.pyi
# repeat for all (~25) u<modules>  
```







<details><summary>Issues already fixed: </summary>
<p>



```

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



</p>
</details> 



