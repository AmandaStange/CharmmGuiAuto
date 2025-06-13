# CharmmGuiAuto

CharmmGuiAuto is a tool designed to automate interactions with CHARMM-GUI, a web-based graphical user interface for CHARMM (Chemistry at HARvard Macromolecular Mechanics), a widely used software for molecular simulations. This tool simplifies the process of preparing input files for molecular dynamics simulations.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Example Input Files](#example-input-files)
- [Known Issues](#known-issues)
- [How to Contribute](#how-to-contribute)
- [Citation](#citation)
- [License](#license)

## Introduction

CHARMM-GUI is a powerful tool for preparing complex molecular systems for simulation, but its web interface can be cumbersome for repetitive tasks. CharmmGuiAuto aims to automate these interactions, streamlining the preparation process and reducing manual input errors.

## Features

- Automates the generation of MD input files using CHARMM-GUI.
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
python CharmmGuiAuto.py -i Example_input_yaml/MembraneProtein.yaml
```

## Example Input Files

The `Example_input_yaml` directory contains sample YAML files that demonstrate how to configure various simulations, and gives an overview of the different parameters that can be changed. You can customize these files to fit your specific needs.

## Known Issues

- Only works with Firefox.
- Cannot be used to continue retrieved jobs, but can download jobs that are finished but not yet downloaded if you have the job ID.
- Firefox binary (`firefox_binary.cpython-37.pyc` - possible original path `miniconda3/lib/python3.7/site-packages/selenium/webdriver/firefox/__pycache__/firefox_binary.cpython-37.pyc`) must be placed in the `bin` of your environment.

## How to Contribute

Contributions are welcome! 

If you would like to contribute:

1. **Fork** this repository.
2. **Clone** your fork locally.
3. **Create a branch** for your changes.
4. **Make your changes**, following PEP 8 style guidelines.
5. **Commit and push** your changes.
6. **Open a pull request**.

For detailed contribution guidelines, please see [CONTRIBUTING.md](CONTRIBUTING.md).

If you plan to contribute **a new feature** or **significant changes**, please open an issue first to discuss your idea.

## Citation

If you use CharmmGuiAuto in your research, please cite the following article:

Stange, A.D., Zuzic, L., Schiøtt, B., & Berglund, N.A. (2025). Exploring insulin-receptor dynamics: Stability and binding mechanisms. *Structure*, 33(8), 1–11. https://doi.org/10.1016/j.str.2025.04.022

BibTeX entry is provided in [citation.bib](citation.bib).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.