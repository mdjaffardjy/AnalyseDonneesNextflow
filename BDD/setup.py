import setuptools 

setuptools.setup( 
    name='AddInDatabase', 
    version='1.0', 
    author='George Marchment & Clemence Sebe', 
    author_email='clemence.sebe@universite-paris-saclay.fr', 
    description='Add in the database all the information on a workflow', 
    packages = setuptools.find_packages(), 
    entry_points={ 
        'console_scripts': [ 
            'AddInDatabase = ScriptBDD.main:main' 
        ]
    }, 
    classifiers=[ 
        'Programming Language :: Python :: 3', 
        'License :: OSI Approved :: MIT License', 
        'Operating System :: OS Independent', 
    ], 
)
