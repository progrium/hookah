from distutils.core import setup

setup(
  name = "hookah",
  version="0.9",
  description="The webhook event broker",
  
  author="Jeff Lindsay",
  author_email="progrium@gmail.com",
  url="http://github.com/progrium/hookah/tree/master",
  download_url="http://github.com/progrium/hookah/tarball/master",
  classifiers=[
    ],
  packages=['hookah'],
  data_files=[('twisted/plugins', ['twisted/plugins/hookah_plugin.py']),
              ('hookah', ['hookah/styles.css'])],
  scripts=['bin/hookah'],
)
