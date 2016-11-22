#!/usr/bin/env python
from distutils.core import setup
setup(name="VFR",
      version="0.1",
      description="Python interface for VFR scene graph library",
      requires=["numpy", "OpenGL"],
      author="Yoshikawa, Hiroyuki, FUJITSU LTD.",
      author_email="yoh@jp.fujitsu.com",
      packages=["VFR"],
  )

