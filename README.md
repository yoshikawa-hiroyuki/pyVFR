# pyVFR
Python interface for VFR scene graph library

## Build
```
  cd vfr
  make -f Makefile.Linux
    or
  make -f Makefile.OSX
```

## Notice
In macOS, wxPython 4.2.1 binary build for Python 3.12 holds a problem with crashes during exit.
To avoid this problem,
- install wxPython from its snapshot-builds. currently, the latest build is <a href="https://wxpython.org/Phoenix/snapshot-builds/wxPython-4.2.2a1.dev5670+a207b407-cp312-cp312-macosx_10_10_universal2.whl">macosx_10_10_universal2.whl</a> .
- build wxPython from development sources.

*updated: 2024/05/04*

## Author
  YOSHIKAWA Hiroyuki, FUJITSU LTD.

