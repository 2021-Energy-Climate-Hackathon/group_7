import numpy as np
import cartopy.io.shapereader as shpreader
from netCDF4 import Dataset
import shapely.geometry


def load_country_weather_data_daily(COUNTRY,data_dir,filename,nc_key,hourflag):

    """
    This function takes the ERA5 reanalysis data, loads it and applied a 
    country mask (ready for conversion to energy) it then returns
    the array (of original size) with all irrelvelant gridpoints 
    set to zeros.

    You will need the shpreader.natural_earth data downloaded 
    to find the shapefiles.

    Args:
        COUNTRY (str): This must be a name of a country (or set of) e.g. 
            'United Kingdom','France','Czech Republic'

        data_dir (str): The parth for where the data is stored.
            e.g '/home/users/zd907959/'

        filename (str): The filename of a .netcdf file
            e.g. 'ERA5_1979_01.nc'

        nc_key (str): The string you need to load the .nc data 
            e.g. 't2m','rsds'
        hourflag (int): This is either 1 or 0, if daily data =0, if
           hourly data = 1.

    Returns:

        country_masked_data (array): Country-masked daily weather data,
            dimensions 
            [time,lat,lon] where there are 0's in locations where the data is 
            not within the country border.

        MASK_MATRIX_RESHAPE (array): Dimensions [lat,lon] where there are 1's if 
           the data is within a country border and zeros if data is outside a 
           country border. 

    """


    # first loop through the countries and extract the appropraite shapefile
    countries_shp = shpreader.natural_earth(resolution='10m',category='cultural',
                                            name='admin_0_countries')
    country_shapely = []
    for country in shpreader.Reader(countries_shp).records():
        if country.attributes['NAME_LONG'] == COUNTRY:
            print('Found country')
            country_shapely.append(country.geometry)

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

    if hourflag == 1: # if hourly data convert to daily
        data = np.mean ( np.reshape(data, (len(data)/24,24,len(lats),len(lons))),axis=1)
        print('Converting to daily-mean')
    if hourflag ==0:
        print('data is daily (if not consult documentation!)')

    LONS, LATS = np.meshgrid(lons,lats) # make grids of the lat and lon data
    x, y = LONS.flatten(), LATS.flatten() # flatten these to make it easier to 
    #loop over.
    points = np.vstack((x,y)).T
    MASK_MATRIX = np.zeros((len(x),1))
    # loop through all the lat/lon combinations to get the masked points
    for i in range(0,len(x)):
        my_point = shapely.geometry.Point(x[i],y[i]) 
        if country_shapely[0].contains(my_point) == True: 
            MASK_MATRIX[i,0] = 1.0 # creates 1s and 0s where the country is
    
    MASK_MATRIX_RESHAPE = np.reshape(MASK_MATRIX,(len(lats),len(lons)))

    # now apply the mask to the data that has been loaded in:

    country_masked_data = data*MASK_MATRIX_RESHAPE
                                     


    return(country_masked_data,MASK_MATRIX_RESHAPE)


def calc_hdd_cdd(t2m_array,country_mask):

    """

    This function takes in an array of country_masked 2m temperature (celsius)
    and converts this into a time series of heating-degree days (HDD) and cooling
    degree days (CDD) using the method from Bloomfield et al.,(2020) 
    https://doi.org/10.1002/met.1858

    Args:

        t2m_array (array): array of country_masked 2m temperatures, Dimensions 
            [time, lat,lon] or [lat,lon] in units of celsius. 
        country_mask (array): array of the country mask applied to the t2m data 
            Dimensions [lat,lon] with 1's for gridpoints within the country.
    Returns:

        HDD_term (array): Dimesions [time], timeseries of heating degree days
        CDD_term (array): Dimesions [time], timeseries of cooling degree days


    """
    len_time = np.shape(t2m_array)[0]

    spatial_mean_t2m =np.zeros(len_time)
    for i in range(0,len_time):
        spatial_mean_t2m[i] = np.average(t2m_array[i,:,:],weights=country_mask)

    # note the function works on daily temperatures. so make sure these are daily!

    HDD_term = np.zeros(len_time)
    CDD_term = np.zeros(len_time)

    for i in range(0,len_time):
        if spatial_mean_t2m[i] <= 15.5:
            HDD_term[i] = 15.5 - spatial_mean_t2m[i]
        else:
            HDD_term[i] =0

    for i in range(0,len_time):
        if spatial_mean_t2m[i] >= 22.0:
            CDD_term[i] = spatial_mean_t2m[i] - 22.0
        else:
            CDD_term[i] =0


    return(HDD_term,CDD_term)


def calc_national_wd_demand_2017(hdd,cdd,filestr_reg_coefficients,COUNTRY):


    """

    This function takes in arrays of national heating-degree days (HDD) 
    and cooling degree days (CDD) using the method from Bloomfield et al.,(2020) 
    https://doi.org/10.1002/met.1858 Combines these with the published 
    regression coefficients to produce weather-dependent demand.
    Regression coefficients are available here for the ERA5 hourly demand model
    https://researchdata.reading.ac.uk/272/

    Args:

        hdd (array): array of national heating degree days, Dimensions 
            [time] 
        cdd (array): array of national cooling degree days, Dimensions 
            [time] 
        filestr_reg_coefficients (string): the filepath of the regression
            coeffients for the dmeand model published here: 
            http://dx.doi.org/10.17864/1947.272
        COUNTRY (string): The country name you wish to calculate demand for
            note that spaces should be underscores e.g. 'Czech_Republic'
           Only the 28 countries that have been modelled in the paper above
           are available.


    """

    all_coeffs = np.genfromtxt(filestr_reg_coefficients,skip_header=1,
                               delimiter=',')
    time_point = 2017. # this is the year the demand model is setup to 
                       # recreate data from.

    # Dictionary saying which country is in which column of the regression
    # coefficent file, filestr_reg_coefficients.
    column_dictionary = {
        "Austria" : 1,
        "Belgium" : 2,
        "Bulgaria" : 3,
        "Croatia" : 4,
        "Czech_Republic" : 5,
        "Denmark" : 6,
        "Finland" : 7,
        "France" : 8,
        "Germany" : 9,
        "Greece" : 10,
        "Hungary" : 11,
        "Ireland" : 12,
        "Italy" : 13,
        "Latvia" : 14,
        "Lithuania" : 15,
        "Luxembourg" : 16,
        "Montenegro" : 17,
        "Netherlands" : 18,
        "Norway" : 19,
        "Poland" : 20,
        "Portugal" : 21,
        "Romania" : 22,
        "Slovakia" : 23,
        "Slovenia" : 24,
        "Spain" : 25,
        "Sweden" : 26,
        "Switzerland" : 27,
        "United_Kingdom" : 28,

    }

    column = column_dictionary[COUNTRY]
    reg_coeffs = all_coeffs[:,column]

    time_coeff = reg_coeffs[0]
    hdd_coeff = reg_coeffs[8]
    cdd_coeff = reg_coeffs[9]
    #weekday_coeff = reg_coeffs[1]

    demand_timeseries = (time_coeff*time_point) + (hdd_coeff*hdd) + (cdd_coeff*cdd)
                  



    return(demand_timeseries)

