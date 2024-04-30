# CharmmGui

Python script to automate the Charmm-Gui process 

required packages:
- selenium
- geckodriver
- yaml
- argparse

COMMENTS/Issues:
- Only works with firefox
- Can be used with 'Solution Builder' with a protein, and the 'Membrane Builder' with or without a protein.
- Can not be used to continue retrieved jobs, but can download jobs that are finished, but not downloaded, if you have the jobid.
- The protonation option is currently broken! 


Firefox binary (firefox_binary.cpython-37.pyc - possible original path 'miniconda3/lib/python3.7/site-packages/selenium/webdriver/firefox/__pycache__/firefox_binary.cpython-37.pyc') must be placed in the bin of your environment.

A yaml file is required as input for the script and there are examples of input files for all three builders (you'll have to add your own email and password for Charmm-Gui)

Command to run:
```
python CharmmGuiAuto.py -i NAME_OF_INPUT_FILE.yaml
```

Suggested command:
```
python -u CharmmGuiAuto.py -i NAME_OF_INPUT_FILE.yaml > NAME_OF_LOG_FILE
```

Please inform me if anything is not working or if any function arguments are not clear
