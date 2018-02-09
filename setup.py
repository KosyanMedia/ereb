from setuptools import setup, find_packages

setup(
    name='ereb',
    description='Tornado based cron with web interface, JSON API and history',
    version='0.18.3',
    url='https://github.com/KosyanMedia/ereb',
    author='Alex Shaikhaleev',
    author_email='nimdraug.sael@gmail.com',
    keywords='tornado web cron',
    packages=['ereb'],
    install_requires=['tornado==4.3', 'crontab==0.22', 'psutil', 'requests', 'datadog'],
    include_package_data=True,
    license='MIT',
    entry_points="""
      [console_scripts]
      ereb = ereb.erebd:main
      """
)
