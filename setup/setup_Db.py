import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/setuptools-0.6c11-py2.4.egg')

try:
    import ez_setup
    ez_setup.use_setuptools()
except:
    pass

from setuptools import setup, find_packages

setup(name="osg-measurements-metrics-db",
      version="1.4",
      author="Brian Bockelman",
      author_email="bbockelm@cse.unl.edu",
      url="http://t2.unl.edu/documentation/gratia_graphs",
      description="DB code - OSG Measurements and Metrics webpages.",

      package_dir={"": "src"},
      packages=['gratia.database','gratia.config'],
      include_package_data=True,
      

      classifiers = [
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: POSIX'
      ],
     
      entry_points={
      },

      data_files=[
	('/etc/', ['config/DBParam.xml.rpmnew']),
      ],
      namespace_packages = ['gratia']
      )


