from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='ncs2_device_plugin',
    version='0.0.1',
    packages=['ncs2_device_plugin'],
    url='https://github.com/adaptant-labs/ncs2-device-plugin',
    license='Apache 2.0',
    author='Adaptant Labs',
    author_email='labs@adaptant.io',
    description='Intel NCS2 device plugin for Kubernetes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=[ 'kubernetes'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Hardware',
        'Topic :: System :: Monitoring',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: Apache Software License',
    ],
    install_requires=requirements,
    entry_points={
        'console_scripts': ['ncs2_device_plugin = ncs2_device_plugin.main:main']
    },
)
