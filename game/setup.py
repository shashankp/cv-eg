from setuptools import setup
 
APP = ['pong.py']
DATA_FILES = ['haarcascade_frontalface_alt.xml']
OPTIONS = {'argv_emulation': False, 'includes': ['pygame', 'cv', 'math', 'random'],
			'excludes': []}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)
