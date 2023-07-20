from setuptools import setup

setup(name='Niralysis',
      version='0.1',
      description='An extensive library for dealing with fNIRS data anylsis.',
      url='https://github.com/Amit-Freiman/Niralysis',
      author='Amit Freiman',
      author_email='amitfreiman@mail.tau.ac.il',
      license='MIT',
      packages=['niralysis'],
      dependency_links=['https://github.com/yoterel/STORM-Net','https://github.com/CMU-Perceptual-Computing-Lab/openpose'],
      install_requires=['snirf','pandas','pathlib','numpy','typing'],
      zip_safe=False)