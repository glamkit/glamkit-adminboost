from setuptools import setup, find_packages

setup(
    name='glamkit-adminboost',
    author='Julien Phalip',
    author_email='julien@interaction.net.au',
    version='0.0.1',
    description='Makes the Django admin even more awesomer',
    url='http://github.com/glamkit/glamkit-admintools',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)