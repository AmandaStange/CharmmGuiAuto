There are 3 different sections, and 3 required options in the input file. The sections are 'system_type', 'system_info', and 'details'. The first two required options are the email and password combination belonging to
the CHARMM-GUI account that is going to be used. This is specified in the input file under 'details':

```sh
details:
  email: ME@MAIL.com
  password: PASSWORD
```

The last required option is the system type. The script can handle 7 different types of systems:
1. Protein in solution (SP)
2. Protein in membrane (MP)
3. Membrane without protein (M)
4. Retrieval of a finished job (R)
5. Reading and manipulation of PDBs (PR)
6. Force field converter (FC)
7. Reading and manipulation of a PDB with an immediate conversion into a different FF (5+6) (RC)

This needs to be specified in the input file under 'system_type'. For a protein in solution that would be:


```sh
system_type:
  system_type: SP
```

The 'system_info' sectionis used to specify if the browser window should be visible(headless: false) or hidden (default, headless: true), and the path where the output should be placed after downloading (path_out)

```sh
system_info:
  headless: true
  path_out: /home/USER/Downloads/
```


The parameters of the 'details' section can be divided into parameters concerning:
- Universal
    download_now (bool): Whether to download the output immediately (default is True).

- PDB manipulation
    pdb_id (str): PDB ID for fetching the file (optional).
    model (any): Model selection options (optional).
    chains (list): List of chains to be patched (optional).
    het (str): Type of non-protein molecule (optional).
    pH (float): Desired pH value (optional).
    preserve (dict): Preserve hydrogen options (default is {'option': None}).
    mutations (list): List of mutations to add (optional).
    protonations (list): List of protonations to add (optional).
    disulfides (list): List of disulfide bonds to add (optional).
    phosphorylations (list): List of phosphorylations to add (optional).
    gpi (dict): GPI anchor options (default is {'GRS': None}).
    glycans (list): List of glycans to add (optional).

- Solvation
    waterbox (dict): Waterbox configuration (default is {'dis': 10.0}).
    ion_method (str): Ion method (optional).

- Membrane
    boxtype (dict): Box type options (optional).
    lengthZ (any): Length in Z direction options (optional).
    lipids (list): List of lipids to add (optional).
    naas (list): List of N-acylated amino acids to add (optional).
    pegs (list): List of PEG lipids to add (optional).
    glycolipids (list): List of glycolipids to add (optional).
    size (int): Size of the system (default is 100).

- Membrane protein
    orientation (str): Orientation option (default is 'PDB').
    position (dict): Position options (default is {'option': None}).
    area (dict): Area options (default is {'option': None}).
    projection (dict): Projection options (default is {'option': None}).

- MD options
    ff (str): Force field type (default is 'c36m').
    engine (str): Simulation engine (default is 'gmx').
    temp (float): Temperature in Kelvin (default is 310).

- Retrieval
    jobid (str): Job ID to retrieve.

- Conversion
    path (str): Directory path where the PSF file is located (optional).
    file_name (str): Name of the PSF file (optional).
    PBC (bool): Whether to set up periodic boundary conditions (default is False).
    PBC_x (float): Size of the PBC box (default is 10).

While this might appear overwhelming it is less so in reality as many of these can be left at their default. For the parameters that have multiple options (such as the protonations) the values should match those written in the dropdown menus of the GUI.

There is an example input file for all system types with each containing comments on the parameters chosen, and if you need help with a specific setup then please just send a message.

It is recommend to run ones system with headless: false, and follow along to ensure the correct options are followed.

 