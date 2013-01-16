from distutils.core import setup
import py2exe

setup(
    name = 'Reader',
    description = 'Reader app for NFC acr122l',
    version = '1.3',

    windows = [
                  {
                      'script': 'reader.py',
                      'icon_resources': [(1, "reader.ico")],
                  }
              ],

    options = {
                  'py2exe': {
                      'packages':'encodings',
                      'includes': 'cairo, pango, pangocairo, atk, gobject, gio, gtk',
                  }
              },
    data_files=[
                   'reader.ico'
               ]
)
