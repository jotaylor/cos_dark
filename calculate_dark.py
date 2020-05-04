import glob
import os
import numpy as np
import pandas as pd
from ftplib import FTP
from astropy.io import fits
from astropy.time import Time
from astropy.io import ascii

__author__ = "Jo Taylor"
__email__ = "jotaylor@stsci.edu"

def measure_darkrate(filename):
    """
    For an input dark dataset, record exposure information including
    observation time, observatory latitude & longitude. Measure dark rate at
    specified regions of the COS FUV detector at a given time interval in order
    to accumulate enough counts for a measurement.
    (Taken from the STScI COS team"s dark monitor, dark_monitor.py, and modified. 
    Original authors include Justin Ely, Mees Fix, Dzhuliya Dashtamirova.)
    
    Args:
        filename (str): Name of dark dataset.
   
    Returns:
        dark_df (:obj:`pandas.dataframe`): Pandas dataframe with information for each
            dark measurement. 
    """

    hdulist = fits.open(filename)

    timeline = hdulist["timeline"].data
    events = hdulist["events"].data
    segment = hdulist[0].header["segment"]
    rootname = hdulist[0].header["rootname"]

    if segment == "FUVA": 
        location = {"inner": (1260, 15119, 375, 660), "bottom": (1060, 15250, 296, 375),
                    "top": (1060, 15250, 660, 734), "left": (1060, 1260, 296, 734),
                    "right": (15119, 15250, 296, 734)}
    elif segment == "FUVB":
        location = {"inner": (1000, 14990, 405, 740), "bottom": (809, 15182, 360, 405),
                    "top": (809, 15182, 740, 785), "left": (809, 1000, 360, 785),
                    "right": (14990, 15182, 360, 785)}
    pha = (2, 23)
    timestep = 25 # in units of seconds
    times = timeline["time"][::timestep].copy()
    events = hdulist["events"].data

    # Creates 5 different tables, one for each region of detector
    d = {}
    for x in location:
        region_area = (location.get(x)[1] - location.get(x)[0]) * (location.get(x)[3] - location.get(x)[2])
        index = np.where((events["PHA"] > pha[0]) &
                         (events["PHA"] < pha[1]) &
                         (events["XCORR"] > location.get(x)[0]) &
                         (events["XCORR"] < location.get(x)[1]) &
                         (events["YCORR"] > location.get(x)[2]) &
                         (events["YCORR"] < location.get(x)[3]))
        unfiltered_pha = np.where((events["XCORR"] > location.get(x)[0]) &
                                  (events["XCORR"] < location.get(x)[1]) &
                                  (events["YCORR"] > location.get(x)[2]) &
                                  (events["YCORR"] < location.get(x)[3]))
        counts = np.histogram(events[index]["time"], bins=times)[0]
        counts_unfiltered_pha = np.histogram(events[unfiltered_pha]["time"], bins=times)[0]
        lat = timeline["latitude"][::timestep][:-1].copy()
        lon = timeline["longitude"][::timestep][:-1].copy()
        second_per_mjd = 1.15741e-5
        mjd_per_step = hdulist[1].header["EXPSTART"] + times.copy().astype(np.float64) * second_per_mjd
        mjd = mjd_per_step[:-1]                                                   
        t = Time(mjd, format="mjd") 
        decyear = t.decimalyear    
        mjdtime = [x.value for x in t]                                               
        counts = counts / region_area / timestep                                             
        counts_unfiltered_pha = counts_unfiltered_pha / region_area / timestep               
        d[x] = pd.DataFrame({"region": x, "segment": segment, "darkrate": counts, "time": mjdtime,
                            "xcorr_min": location.get(x)[0], "xcorr_max": location.get(x)[1],    
                             "ycorr_min": location.get(x)[2], "ycorr_max": location.get(x)[3],   
                             "longitude": lon, "latitude": lat, "rootname": rootname, 
                             "unfiltered_pha_counts": counts_unfiltered_pha})    
    # Combine all 5 tables for different regions                                  
    dark_df = pd.concat([d["inner"], d["bottom"], d["top"], d["left"], d["right"]])       
    # Flag data taken near SAA where flag=1 denotes data outside the SAA.
    dark_df["saa_flag"] = np.where(dark_df.eval("latitude > 10 or longitude < 260"), 1, 0)
    hdulist.close() 
    
    return dark_df

def get_solar_data(solardir):
    """
    Pull solar data files from NOAA website. Solar data is FTPd from NOAA and 
    written to text files.
    (Taken from the STScI COS team"s dark monitor, dark_monitor.py, and modified. 
    Original authors include Justin Ely, Mees Fix, Dzhuliya Dashtamirova.)

    Args:
        solardir (str): Directory to write the solar data files to.
    """

    ftp = FTP("ftp.swpc.noaa.gov")
    ftp.login()
    ftp.cwd("/pub/indices/old_indices/")

    for item in sorted(ftp.nlst()):
        if item.endswith("_DSD.txt"):
            year = int(item[:4])
            if year >= 2008:
                print("Retrieving: {}".format(item))
                destination = os.path.join(solardir, item)
                ftp.retrbinary("RETR {}".format(item),
                               open(destination, "wb").write)
                os.chmod(destination, 0o777)

def parse_solar_files(files):
    """
    Parse solar data text files and return date and flux.
    (Taken from the STScI COS team"s dark monitor, dark_monitor.py, and modified. 
    Original authors include Justin Ely, Mees Fix, Dzhuliya Dashtamirova.)
    
    Args:
        files (str or array-like): If a string, a check is done to see if string 
            is a file or a directory to be globbed. If not a string, array-like
            is assumed.
    
    Returns:
        date (:obj:`numpy.ndarray`): MJD of each solar flux measurement.
        flux (:obj:`numpy.ndarray`): Solar flux measurements.
    """

    date = []
    flux = []
    if isinstance(files, str):
        if os.path.isfile(files):
            input_list = [files]
        else:
            input_list = glob.glob(os.path.join(files, "*DSD.txt"))
    else:
        input_list = files
    input_list.sort()

    for item in input_list:
        print("Reading {}".format(item))

        # clean up Q4 files when year-long file exists
        if ("Q4_" in item) and os.path.exists(item.replace("Q4_", "_")):
            print("Removing duplicate observations: {}".format(item))
            os.remove(item)
            continue

        # astropy.ascii no longer returns an empty table for empty files
        # Throws IndexError, we will go around it if empty.
        try:
            data = ascii.read(item, data_start=1, comment="[#,:]")
        except IndexError:                                    
            continue                                          
                                                              
        for line in data:                                     
            line_date = Time("{}-{}-{} 00:00:00".format(line["col1"],       
                                                        line["col2"],       
                                                        line["col3"]),      
                             scale="utc", format="iso").mjd   
            line_flux = line[3]                               
                                                              
            if line_flux > 0:                                 
                date.append(line_date)                        
                flux.append(line_flux)                        
                                                              
    return np.array(date), np.array(flux)                     

