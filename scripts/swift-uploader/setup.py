import setuptools

setuptools.setup(
    name='crawl_uploader',
    version='0.1',
    description='DOS Attacker Crawler Result Uploader',
    author='Alistair King, Mingwei Zhang',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'python-dotenv',
        'argparse',
        'python-swiftclient'
    ],
    entry_points={'console_scripts': [
        # updater tool
        "crawl-uploader = uploader.main:main",
    ]}
)
