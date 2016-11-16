from setuptools import setup, find_packages

setup(
    name='ereb',
    description='Tornado based cron with web interface, JSON API and history',
    version='0.16.5',
    url='https://github.com/KosyanMedia/ereb',
    author='Alex Shaikhaleev',
    author_email='nimdraug.sael@gmail.com',
    keywords='tornado web cron',
    packages=find_packages(),
    install_requires=['tornado==4.3', 'crontab', 'psutil'],
    license='MIT',
    scripts=['ereb', 'lib']
)
