import setuptools 

setuptools.setup( 
    name='extractNF', 
    version='1.0', 
    author='George Marchment & Clemence Sebe', 
    author_email='george.marchment@universite-paris-saclay.fr', 
    description='Extracts a certain amount of information from one or multiple nextflow workflows', 
    packages=setuptools.find_packages(), 
    entry_points={ 
        'console_scripts': [ 
            'NFanalyzer = Scripts.main:main' 
        ]
    }, 
    classifiers=[ 
        'Programming Language :: Python :: 3', 
        'License :: OSI Approved :: MIT License', 
        'Operating System :: OS Independent', 
    ], 
)
