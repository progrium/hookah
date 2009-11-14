from setuptools import setup

setup(
  name = "hookah",
  version="0.1.0",
  description="Scalable async HTTP request dispatcher",
  
  author="Jeff Lindsay",
  author_email="progrium@gmail.com",
  url="http://github.com/progrium/hookah/tree/master",
  download_url="http://github.com/progrium/hookah/tarball/master",
  classifiers=[
    ],
  packages=['hookah'],
  data_files=[('twisted/plugins', ['twisted/plugins/hookah_plugin.py'])],
  scripts=['bin/hookah'],
  install_requires = [
      'pyyaml>=3',
  ],
)
