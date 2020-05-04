# COS Dark Characterization

## Another background correction?
COS spectroscopic science in the extreme UV regime is limited by detector 
background noise. The COS pipeline, `calcos` does not perform an optimized 
background subtraction. In order to achieve the maximum scientific value of
the COS instrument, we have a designed a custom characterization and correction
of the COS FUV dark rate.

To measure the dark rate as a function of time and position, a complete
database with observation information is necessary. This code creates
and updates this database, `cos_dark.db`.

## Installation
If you do not already have Conda installed, you need to download install
either Miniconda or Anaconda. Miniconda provides a bare-minimum Conda
environment. Anaconda provides a full Conda root environment along with
many other tools, libraries, and utilities.
* get [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
* get [Anaconda](https://www.anaconda.com/products/individual)

Now clone this repository on your local machine. Do this by typing:
`git clone git@github.com:spacetelescope/jwst.git`
for SSH connection, or:
`git clone https://github.com/spacetelescope/jwst.git`
for HTTPS connection.

### Installing into a fresh environment
Now, go to the cloned directory and from a bash shell enter:

```
conda create -n <env_name> python
conda activate <env_name>
pip install -e .
```

This only installs packages needed for the `cos_dark` software. You will
need to install anything else, e.g.:

```
pip install ipython scipy asdf
```

### Installing into an existing environment
Go to the cloned directory and from a bash shell enter:

```
pip install -e . 
```

## Usage

If you are within the STScI network you can create the database necessary 
to analyze the dark rate like so:

```
python create_db.py
python update_db.py
```

If you are outside the STScI network, you can use the sqlite3 database 
in this package: `cos_dark.db`.

To access the database, you will need [SQLite](https://www.sqlite.org/index.html) 
if you do not already have it.

Simply type:

```
sqlite3 cos_dark.db
```

and start exploring! For tips on SQLite queries, click [here](https://www.tutorialspoint.com/sqlite/sqlite_select_query.htm).

The format of the database is as follows:

**Darks**
| column                  | type    | description                     |
| ----------------------- | ------- | ------------------------------- |
| id                      | Integer | Primary key ID number           |
| filename                | String  | E.g. ipppssoot_corrtag_a.fits   |
| rootname                | String  | E.g. ipppssoot                  |
| segment                 | String  | COS FUV segment                 |
| expstart                | Float   | MJD start time                  |
| exptime                 | Float   | Exposure time (s)               |
| hva                     | Integer | High Voltage for FUVA           |
| hvb                     | Integer | High Voltage for FUVB           |
| latitude                | Float   | Observatory latitude            |
| longitude               | Float   | Observatory longitude           |
| darkrate                | Float   | Dark counts/s                   |
| time                    | Float   | Time for each darkrate value    |
| region                  | String  | Detector region for dark rate   |
| xcorr_min               | Integer | Region starting XCORR           |
| xcorr_max               | Integer | Region ending XCORR             |
| ycorr_min               | Integer | Region staring YCORR            |
| ycorr_max               | Integer | Region ending YCORR             |
| saa_flag                | Integer | Data near SAA = 0, else 1       |
| unfiltered_pha_counts   | Float   | Counts not filtered by PHA      |
| solar_flux              | Float   | Solar flux at each sampled time |
| fileloc                 | String  | STScI disk location of file     |

**Solar**
| column | type  | description                        |
| ------ | ----- | ---------------------------------- |
| time   | Float | MJD date of solar flux measurement |
| flux   | Float | 10.7cm radio flux                  |

Solar flux values are obtained from [NOAA](https://www.swpc.noaa.gov/phenomena/f107-cm-radio-emissions).
