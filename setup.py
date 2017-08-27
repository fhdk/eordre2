from distutils.core import setup

setup(
    name='eordre-app.pyqt',
    version='0.2.1',
    packages=['', 'util', 'models', 'dialogs', 'resources', 'configuration'],
    url='https://github.com/fhdk/eordre-app.pyqt',
    license='AGPL',
    author='Frede Hundewadt',
    author_email='fh@uex.dk',
    description='Eordre app build with Python 3 and PyQt5',
    requires=['PyQt5']
)
