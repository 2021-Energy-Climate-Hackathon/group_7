import numpy as np
from netCDF4 import Dataset

def load_100mwindspeed_data(data_dir,filename):

    """
    This function takes the ERA5 reanalysis data, loads it and applied a 
    country mask (ready for conversion to energy) it then returns
    the array (of original size) with all irrelvelant gridpoints 
    set to zeros.

    You will need the shpreader.natural_earth data downloaded 
    to find the shapefiles.

    Args:

        data_dir (str): The parth for where the data is stored.
            e.g '/home/users/zd907959/'

        filename (str): The filename of a .netcdf file
            e.g. 'ERA5_1979_01.nc'

    Returns:

        wind_speed_data (array): 100m wind speed data, dimensions 
            [time,lat,lon].

    """

  
    # load in the data you wish to mask
    file_str = data_dir + filename
    dataset = Dataset(file_str,mode='r')
    lons = dataset.variables['longitude'][:]
    lats = dataset.variables['latitude'][:]
    data1 = dataset.variables['u100'][:] # data in shape [time,lat,lon]
    data2 = dataset.variables['v100'][:] # data in shape [time,lat,lon]
    dataset.close()

    wind_speed_data = np.sqrt(data1*data1 + data2*data2)

    return(wind_speed_data)



def meanBC_wind_speed_data(wind_speed_data,bias_correction_file):

    """
    This function takes the ERA5 reanalysis data, loads it and applied a 
    country mask (ready for conversion to energy) it then returns
    the array (of original size) with all irrelvelant gridpoints 
    set to zeros.

    You will need the shpreader.natural_earth data downloaded 
    to find the shapefiles.

    Args:

        wind_speed_data (array): 100m wind speed  data, dimensions 
            [time,lat,lon]

        bias_correction_file (str): The filename of a .npy file
            containing the mean Bias correction factors on this grid.

    Returns:

        BC_wind_speed_data (array): 100m wind speed  data, dimensions 
            [time,lat,lon] with a mean bias correction calcualted based on the
            Global Wind Atlas data applied. globalwindatlas.info

    """

    correction_factors = np.load(bias_correction_file)

    len_time = np.shape(wind_speed_data)[0]
    BC_wind_speed_data = np.zeros(np.shape(wind_speed_data))
    for i in range(0,len_time):
        BC_wind_speed_data[i,:,:] = wind_speed_data[i,:,:] + correction_factors
    # set any times when the wind speed drops below zero to zero.
    

    BC_wind_speed_data[BC_wind_speed_data <0.] = 0.
    
    return(BC_wind_speed_data)





def convert_to_windpower(wind_speed_data,power_curve_file):

    """
    This function takes the ERA5 reanalysis data, loads it and applied a 
    country mask (ready for conversion to energy) it then returns
    the array (of original size) with all irrelvelant gridpoints 
    set to zeros.

    You will need the shpreader.natural_earth data downloaded 
    to find the shapefiles.

    Args:

        gridded_wind_power (array): wind power capacity factor data, dimensions 
            [time,lat,lon]. Capacity factors range between 0 and 1.

        power_curve_file (str): The filename of a .csv file
            containing the wind speeds (column 0) and capacity factors 
            (column 2) of the chosen wind turbine.

    Returns:

        wind_power_cf (array): Gridded wind Power capacity factor  
            data, dimensions [time,lat,lon]. Values vary between 0 and 1.

    """

    # first load in the power curve data
    pc_w = []
    pc_p = []

    with open(power_curve_file) as f:
        for line in f:
            columns = line.split()
            #print columns[0]
            pc_p.append(np.float(columns[2]))  
            pc_w.append(np.float(columns[0]))  # get power curve output (CF)

    # convert to an array
    power_curve_w = np.array(pc_w)
    power_curve_p = np.array(pc_p)

    #interpolate to fine resolution.
    pc_winds = np.linspace(0,50,501) # make it finer resolution 
    pc_power = np.interp(pc_winds,power_curve_w,power_curve_p)

    reshaped_speed = wind_speed_data.flatten()
    test = np.digitize(reshaped_speed,pc_winds,right=False) # indexing starts 
    #from 1 so needs -1: 0 in the next bit to start from the lowest bin.
    test[test ==len(pc_winds)] = 500 # make sure the bins don't go off the 
    #end (power is zero by then anyway)
    wind_power_flattened = 0.5*(pc_power[test-1]+pc_power[test])

    wind_power_cf = np.reshape(wind_power_flattened,(np.shape(wind_speed_data)))
    
    return(wind_power_cf)






def convert_to_windpower_optimal_turbine(wind_speed_data,optimal_turbines,power_curve_file1,power_curve_file2,power_curve_file3):
    
    """
    This function takes the ERA5 reanalysis data, loads it and applied a 
    country mask (ready for conversion to energy) it then returns
    the array (of original size) with all irrelvelant gridpoints 
    set to zeros.

    You will need the shpreader.natural_earth data downloaded 
    to find the shapefiles.

    Args:

        wind_speed_data (array): 100m wind speed data, dimensions 
            [time,lat,lon].

        optimal_turbines (str): The filename of a .nc file
            containing the optimal class of wind turbine to install in each 
            ERA5 gridbox.

        power_curve_file1 (str): The filename of a .csv file
            containing the wind speeds (column 0) and capacity factors 
            (column 2) of the class 1 wind turbine
 
       power_curve_file2 (str): The filename of a .csv file
            containing the wind speeds (column 0) and capacity factors 
            (column 2) of the class 2 wind turbine

       power_curve_file3 (str): The filename of a .csv file
            containing the wind speeds (column 0) and capacity factors 
            (column 2) of the class 3 wind turbine

    Returns:

        wind_power_cf (array): Gridded wind Power capacity factor  
            data, dimensions [time,lat,lon]. Values vary between 0 and 1.

    """

    # Load is the class 1 wind turbine
    pc_w1 = []
    pc_p1 = []

    with open(power_curve_file1) as f:
        for line in f:
            columns = line.split()
            #print columns[0]
            pc_p1.append(np.float(columns[2]))  
            pc_w1.append(np.float(columns[0])) 

    # convert to an array
    power_curve_w1 = np.array(pc_w1)
    power_curve_p1 = np.array(pc_p1)

    # Load in the class 2 wind turbine
    pc_w2 = []
    pc_p2 = []

    with open(power_curve_file2) as f:
        for line in f:
            columns = line.split()
            #print columns[0]
            pc_p2.append(np.float(columns[2]))  
            pc_w2.append(np.float(columns[0]))  

    # convert to an array
    power_curve_w2 = np.array(pc_w2)
    power_curve_p2 = np.array(pc_p2)

    # Load in the class 3 wind turbine
    pc_w3 = []
    pc_p3 = []

    with open(power_curve_file3) as f:
        for line in f:
            columns = line.split()
            #print columns[0]
            pc_p3.append(np.float(columns[2]))  
            pc_w3.append(np.float(columns[0]))  

    # convert to an array
    power_curve_w3 = np.array(pc_w3)
    power_curve_p3 = np.array(pc_p3)


    #interpolate to fine resolution.
    pc_winds = np.linspace(0,50,501) # make it finer resolution 
    pc_power1 = np.interp(pc_winds,power_curve_w1,power_curve_p1)
    pc_power2 = np.interp(pc_winds,power_curve_w2,power_curve_p2)
    pc_power3 = np.interp(pc_winds,power_curve_w3,power_curve_p3)

    # load in the turbine type data.
    turbine_type_data = Dataset(optimal_turbines,mode='r')
    turbine_totals = turbine_type_data.variables['totals'][:]
    turbine_type_data.close()

    # predefine an array to story the cf data in
    len_timeseries = np.shape(wind_speed_data)[0]
    wind_power_cf = np.zeros(np.shape(wind_speed_data))
    
    # calcualte cf at each timetep
    for i in range(0,len_timeseries):
        
        reshaped_speed = wind_speed_data[i,:,:].flatten()
        totals = turbine_totals.flatten()
        test = np.digitize(reshaped_speed,pc_winds,right=False) # indexing starts       #from 1 so needs -1: 0 in the next bit to start from the lowest bin.
        test[test ==len(pc_winds)] = 500 # make sure the bins don't go off the 
        #end (power is zero by then anyway)

        wind_power_class1 = 0.5*(pc_power1[test-1]+pc_power1[test])
        wind_power_class2 = 0.5*(pc_power2[test-1]+pc_power2[test])
        wind_power_class3 = 0.5*(pc_power3[test-1]+pc_power3[test])

        # put as zero at gridpoints where we shouldnt be using this class.
        wind_power_class1[totals ==2]=0
        wind_power_class1[totals ==3]=0

        wind_power_class2[totals ==1]=0
        wind_power_class2[totals ==3]=0
 
        wind_power_class3[totals ==1]=0
        wind_power_class3[totals ==2]=0

        
        wind_power = wind_power_class1 + wind_power_class2 +  wind_power_class3
        wind_power_cf[i,:,:] = np.reshape(wind_power,(np.shape(wind_speed_data[i,:,:])))
    return(wind_power_cf)





def country_wind_power(gridded_wind_power,wind_turbine_locations):

    """
    This function takes the ERA5 reanalysis data, loads it and applied a 
    country mask (ready for conversion to energy) it then returns
    the array (of original size) with all irrelvelant gridpoints 
    set to zeros.

    You will need the shpreader.natural_earth data downloaded 
    to find the shapefiles.

    Args:

        gridded_wind_power (array): wind power capacity factor data, dimensions 
            [time,lat,lon]. Capacity factors range between 0 and 1.

        wind turbine locations (str): The filename of a .nc file
            containing the amount of installed wind power capacity in gridbox

    Returns:

        wind_power_country_cf (array): Time series of wind Power capacity factor              data, weighted by the installed capacity in each reanalysis
            gridbox from thewindpower.net database. dimensions [time]. 
            Values vary between 0 and 1.

    """

    # first load in the installed capacity data.

 
    dataset_1 = Dataset(wind_turbine_locations,mode='r')
    total_MW = dataset_1.variables['totals'][:]
    dataset_1.close()

    len_timeseries = np.shape(gridded_wind_power)[0]

    wind_power_country_cf = np.zeros(len_timeseries)

    for i in range(0,len_timeseries):
        wind_power_weighted = gridded_wind_power[i,:,:]*total_MW
        wind_power_country_cf[i] = np.sum(wind_power_weighted)/np.sum(total_MW)

    
    return(wind_power_country_cf)




