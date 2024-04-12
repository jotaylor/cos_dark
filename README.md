# Another COS Dark Correction (ACDC) ⚡

## Another dark correction?
COS spectroscopic science in the extreme UV regime is limited by detector 
background noise. The COS pipeline, 
[`CalCOS`](https://github.com/spacetelescope/calcos) 
performs a basic background subtraction, but for low signal-to-noise ratio (SNR)
observations, a more nuanced approach is necessary to fully capitalize on COS's
FUV capabilities. In order to achieve the maximum scientific value of
the COS instrument, we have a designed a custom
characterization and correction of the COS FUV dark rate, `acdc`.

With `acdc`, we can: 
* create and maintain databases needed to measure the dark rate as a function of time, HST position, PHA, solar activity, and more
* create COS/FUV superdarks
* use superdarks to perform custom dark corrections
* analyze the efficacy of custom dark-corrected COS data

## Installation

### Create a conda Environment
If you do not already have Conda installed, you need to download and install
either Miniconda or Anaconda. Miniconda provides a bare minimum Conda
environment. Anaconda provides a full Conda root environment along with
many other tools, libraries, and utilities.
* get [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
* get [Anaconda](https://www.anaconda.com/products/individual)

Create a conda enviornment to use `acdc`:

```
conda create -n <env_name> python=<version>
conda activate <env_name>
pip install .
```

where `<env_name>` is the name of the environment that will be created.
You need at least python version 3.9, so fill in `<version>` with whatever
version >=3.9 that you desire.

### Install the latest stable version
The easiest way to install `acdc` is to use `pip`:

```
pip install acdc-hst
```

> ⚠️ **Note**
> 
> The [package name on PyPi](https://pypi.org/project/acdc-hst/) and the name of this repo,
> `acdc-hst`, is different than the _imported_ package name, `acdc`. That is,
> you import the package as `import acdc`.

### Install the development version

First clone this repo. Then `cd` into the cloned repository and execute:

```
pip install .
```

To install requirements for building the sphinx documentation:

```
pip install ".[docs]"
```

## Usage

For full usage instructions, refer to the documentation. 

## Building the docs
First clone this repository, then navigate into the repo and
the `docs/` directory. Once there, run the following command:

```
make html
```

It will take a minute or two to build all the docs. Once finished, you can open the 
docs in your default web browser with the following command:

```
open _build/html/index.html 
```

From there you can click and navigate the webpage as if it were hosted online normally.
