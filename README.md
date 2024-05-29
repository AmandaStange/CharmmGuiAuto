
# CharmmGuiAuto

CharmmGuiAuto is a tool designed to automate interactions with CHARMM-GUI, a web-based graphical user interface for CHARMM (Chemistry at HARvard Macromolecular Mechanics), a widely used software for molecular simulations. This tool simplifies the process of preparing input files for molecular dynamics simulations.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Example Input Files](#example-input-files)
- [License](#license)

## Introduction

CHARMM-GUI is a powerful tool for preparing complex molecular systems for simulation, but its web interface can be cumbersome for repetitive tasks. CharmmGuiAuto aims to automate these interactions, streamlining the preparation process and reducing manual input errors.

## Features

- Automates the generation of input files for CHARMM-GUI.
- Simplifies the preparation of molecular dynamics simulations.
- Provides a set of example YAML files for easy customization.
- Integrates seamlessly with CHARMM-GUI web interface.

## Installation

To install CharmmGuiAuto, clone the repository and install the required dependencies:

```sh
git clone https://github.com/AmandaStange/CharmmGuiAuto.git
cd CharmmGuiAuto
micromamba create -n charmmauto -f requirements.txt -c conda-forge
micromamba activate charmmauto
```

## Usage

Here is a basic example of how to use CharmmGuiAuto:

1. Prepare your input YAML file. You can start with one of the examples provided in the `Example_input_yaml` directory.
2. Run the script with your YAML file as input.

```sh
python CharmmGuiAuto.py -i Example_input_yaml/new_example.yaml
```

## Example Input Files

The `Example_input_yaml` directory contains sample YAML files that demonstrate how to configure various simulations. You can customize these files to fit your specific needs.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
