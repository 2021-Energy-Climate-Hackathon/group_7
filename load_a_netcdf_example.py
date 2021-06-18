import numpy as np
from netCDF4 import Dataset

def load_weather_data_daily(data_dir,filename,nc_key):

    """
    This function takes the ERA5 reanalysis data and loads it.

    Args:
        data_dir (str): The parth for where the data is stored.
            e.g '/home/users/zd907959/'

        filename (str): The filename of a .netcdf file
            e.g. 'ERA5_1979_01.nc'

        nc_key (str): The string you need to load the .nc data 
            e.g. 't2m','rsds'


    Returns:

        weather_data (array): Country-masked daily weather data,
            dimensions 
            [time,latitude,longitude] where there are 0's in locations where the data is 
            not within the country border.

        lat_data (array): Dimensions [latitude]  The latitudes of the array

        lon_data (array): Dimensions [longitude]  The longitudes of the array


    """
 
    # load in the data you wish to mask
    file_str = data_dir + filename
    dataset = Dataset(file_str,mode='r')
    lons = dataset.variables['longitude'][:]
    lats = dataset.variables['latitude'][:]
    data = dataset.variables[nc_key][:] # data in shape [time,lat,lon]
    dataset.close()

    # get data in appropriate units for models
    if nc_key == 't2m':
        data = data-273.15 # convert to Kelvin from Celsius
    if nc_key == 'ssrd':
        data = data/3600. # convert Jh-1m-2 to Wm-2
                            


    return(data,lons,lats)





##############
#
# Main code
#
##############

ERA5_data_jan_1979,lats,lons = load_weather_data_daily('/storage/silver/S2S4E/energymet/ERA5/native_grid_hourly/','ERA5_1hr_1979_01_DET.nc','t2m')


