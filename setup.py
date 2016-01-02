from setuptools import setup

exec(open("./difference_polygons/_version.py").read())

setup(
    name="difference-polygons",
    version=__version__,
    author="Rory McCann",
    author_email="rory@technomancy.org",
    packages=['difference_polygons'],
    platforms=['any',],
    requires=[
        "fiona",
        "shapely"
    ],
    entry_points={
        'console_scripts': [
            'difference-polygons= difference_polygons:main',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
    ],
)
