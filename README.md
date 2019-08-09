# fuzzy_schemas

## Fuzzy mapping schemas for several hazards developed within the project RIESGOS 

In the folder "lib" there are the python modules implementing the basic properties of fuzzy numbers (file fuzzy.py) and the 
functions for the fuzzy scoring (file scoring.py)

In the folder schema_scripts there are the ipython notebooks with the implementation of the single schemas. Each folder has an "output" 
folder where the output files (also temporary images) are stored.

The output fuzzy schemas (in json or yaml format) are stored in the "schemas" folder. 

Example:
<pre>
.
├── data
│   └── survey_09_14122018_completed.csv
├── lib
│   └── fuzzy_scoring
│       ├── __init__.py
│       ├── __init__.pyc
│       ├── fuzzy.py
│       ├── fuzzy.pyc
│       ├── scoring.py
│       └── scoring.pyc
├── schema_scripts
│   └── Valpo_test
│       ├── Valpotest.ipynb
│       └── output
│           ├── s_09_valp2018_bdg599_ems98.png
│           ├── s_09_valp2018_bdg599_hazus.png
│           ├── valpo_test_ems98_schema.png
│           └── valpo_test_hazus_schema.png
└── schemas
    ├── valpo_test_ems98.json
    └── valpo_test_hazus.json
</pre>
