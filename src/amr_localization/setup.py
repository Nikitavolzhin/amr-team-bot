from setuptools import find_packages, setup


package_name = "amr_localization"


setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        (
            "share/" + package_name,
            ["package.xml"],
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Ashraful",
    maintainer_email="ashrafulhossainwork@gmail.com",
    description=(
        "Created a custom particle-filter localization package "
        "for our AMR project."
    ),
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            (
                "particle_filter_node = "
                "amr_localization.particle_filter_node:main"
            ),
        ],
    },
)