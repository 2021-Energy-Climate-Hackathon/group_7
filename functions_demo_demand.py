import energy_model_functions_demand as energy_model_functions
import matplotlib.pyplot as plt
import numpy as np



#
#
# DEMAND MODEL EXAMPLE
#
#
#
country = 'Austria' # pre-define this to make sure it is the same in all the functions below, if not the results will not make sense. 

t2m_data,country_mask = energy_model_functions.load_country_weather_data_daily(country,'/storage/silver/S2S4E/energymet/ERA5/native_grid_hourly/','ERA5_1hr_1979_01_DET.nc','t2m',1)

hdd, cdd = energy_model_functions.calc_hdd_cdd(t2m_data,country_mask)

demand_timeseries = energy_model_functions.calc_national_wd_demand_2017(hdd,cdd,'/home/users/zd907959/code_folders/CLEARHEADS/S2S4E_model_code_python_functions/ERA5_Regression_coeffs_demand_model.csv',country)


