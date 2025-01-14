#!/usr/bin/env python
from setuptools import setup
setup(name="VFR",
      version="0.1.2",
      description="Python interface for VFR scene graph library",
      requires=["numpy", "OpenGL", "wx"],
      author="Yoshikawa, Hiroyuki, FUJITSU LTD.",
      author_email="yoh@jp.fujitsu.com",
      packages=["VFR"],
  )

