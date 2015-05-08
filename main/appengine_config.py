# coding: utf-8

import os
import sys


if os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Engine'):
  sys.path.insert(0, 'lib.zip')
else:
  import re
  from google.appengine.tools.devappserver2.python import stubs
  try:
    re_ = stubs.FakeFile._skip_files.pattern.replace('|^lib/.*', '')
    re_ = re.compile(re_)
    stubs.FakeFile._skip_files = re_
  except AttributeError:
    print "[appengine_config] Replace lib didn't work"
  sys.path.insert(0, 'lib')
sys.path.insert(0, 'libx')
