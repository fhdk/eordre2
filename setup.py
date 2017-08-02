from distutils.core import setup

setup(
    name='eordre-app.pyqt',
    version='0.1.1',
    packages=['', 'util', 'models', 'dialogs', 'resources', 'configuration'],
    url='https://github.com/fhdk/eordre-app.pyqt.pyqt',
    license='AGPL',
    author='Frede Hundewadt',
    author_email='fh@uex.dk',
    description='Eordre app builders with python and pyqt',
    requires=['PyQt5']
)
