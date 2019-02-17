from setuptools import setup

setup(name='easy_rosetta',
      version='0.1',
      description='A CLI to automate Rosetta AbinitioRelax protocol and analyze the results on Berkeley Savio clusters',
      url='http://github.com/walterwu/easy_rosetta',
      author='Walter Wu',
      author_email='walter.wu@berkeley.edu',
      license='MIT',
      packages=['easy_rosetta'],
      include_package_data=True,
      entry_points = {
        'console_scripts': [
        'easy-rosetta-config=easy_rosetta.main:config',
        'easy-rosetta-runall=easy_rosetta.main:runall',
        'easy-rosetta-postprocess=easy_rosetta.main:postprocess',
        'easy-rosetta-fragment-picker=easy_rosetta.main:fragment_picker',
        'easy-rosetta-abinitio-relax=easy_rosetta.main:abinitio_relax',
        'easy-rosetta-score=easy_rosetta.main:score',
        'easy-rosetta-cluster=easy_rosetta.main:cluster',
        ],
      },
      zip_safe=False)