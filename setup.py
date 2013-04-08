from setuptools import setup, find_packages


version = '1.0.dev0'


setup(name='plonesource',
      version=version,
      description='Directory of Plone core and add-on sources'
      ' for buildout / mr.developer.',

      classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='plonesource',
      author='Jonas Baumann',
      author_email='mailto:tschouns@gmail.com',
      url='https://github.com/jone/plonesource.org',

      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'pygithub3',
        ],

      entry_points = {
        'console_scripts' : ['update = plonesource.update:main']
        })
