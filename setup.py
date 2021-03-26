import os, subprocess
from setuptools import setup
from gaspar import __version__ as version

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def get_requires(rfile):
    """Get list of required Python packages."""
    requires = list()
    with open(rfile, "r") as reqfile:
        for line in reqfile.readlines():
            requires.append(line.strip())
    return requires



setup(
    name = "gaspar",
    version = version,
    author = "UltraDesu",
    author_email = "ultradesu@hexor.ru",
    description = ("Telegram bot. Keep an eye on rutracker.org topics and let you "
                                   "know if it has been updated."),
    license = "WTFPL",
    keywords = "telegram bot",
    url = "https://github.com/house-of-vanity/gapsar",
    packages=['gaspar'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
    entry_points={
        'console_scripts': [
            'gaspar = gaspar.gaspar:main',
        ]
    },
    data_files=[
        ("/usr/share/gaspar", ['gaspar/scheme.sql']),
    ],
    install_requires=get_requires("./requirements.txt")
)

os.umask(0o666)
subprocess.call(['chmod', '-R', 'a+rwX', '/usr/share/gaspar'])
