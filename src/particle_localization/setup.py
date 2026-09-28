from setuptools import find_packages, setup

package_name = 'particle_localization'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        (
            'share/' + package_name,
            ['package.xml'],
        ),
        (
            'share/' + package_name + '/config',
            ['config/particle_filter.yaml'],
        ),
    ],
    install_requires=['setuptools', 'numpy'],
    zip_safe=True,
    maintainer='Ashraful',
    maintainer_email='ashrafulhossainwork@gmail.com',
    description='Monte Carlo particle filter localization for the Robile robot.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'particle_filter = particle_localization.particle_filter:main',
        ],
    },
)
