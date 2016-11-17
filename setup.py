from setuptools import setup, find_packages

setup(
    name='ereb',
    description='Tornado based cron with web interface, JSON API and history',
    version='0.16.7',
    url='https://github.com/KosyanMedia/ereb',
    author='Alex Shaikhaleev',
    author_email='nimdraug.sael@gmail.com',
    keywords='tornado web cron',
    packages=['lib'],
    install_requires=['tornado==4.3', 'crontab', 'psutil'],
    include_package_data=True,
    license='MIT',
    scripts=['ereb']
)
