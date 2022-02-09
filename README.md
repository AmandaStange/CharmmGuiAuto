# CharmmGui

Python script to automate the Charmm-Gui process 

required packages:
- selenium
- geckodriver
- yaml

COMMENTS/Issues:
- Only works with firefox
- Can be used with 'Solution Builder' with a protein, and the 'Membrane Builder' with or without a protein.
- Can not be used on retrieved jobs (only if you modify it yourself which you are welcome to do)
- For protein only uploads work not PDB ID.

Firefox binary (firefox_binary.cpython-37.pyc - possible original path 'miniconda3/lib/python3.7/site-packages/selenium/webdriver/firefox/__pycache__/firefox_binary.cpython-37.pyc') must be placed in the bin of your environment.

A yaml file is required as input for the script and there are examples of input files for all three builders

Command to run:
```
python CharmmGuiAuto.py NAME_OF_INPUT_FILE
```

Suggested command:
```
python -c CharmmGuiAuto.py NAME_OF_INPUT_FILE > NAME_OF_LOG_FILE
```

Please inform me if anything is not working or if any function arguments are not clear
