import setuptools 

setuptools.setup( 
    name='ProSim', 
    version='1.0', 
    author='George Marchment & Clemence Sebe', 
    author_email='george.marchment@universite-paris-saclay.fr', 
    description='Calculates the similarity between multiple processes', 
    packages = setuptools.find_packages(), 
    entry_points={ 
        'console_scripts': [ 
            'ProSim = Script.main:main' 
        ]
    }, 
    classifiers=[ 
        'Programming Language :: Python :: 3', 
        'License :: OSI Approved :: MIT License', 
        'Operating System :: OS Independent', 
    ], 
)
