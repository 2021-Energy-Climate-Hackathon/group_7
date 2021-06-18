import energy_model_functions_wind_power as energy_model_functions
import matplotlib.pyplot as plt
import numpy as np


#
#
#
# WIND POWER EXAMPLE
#
#
#

speed100m_data = energy_model_functions.load_100mwindspeed_data('/storage/silver/S2S4E/energymet/ERA5/native_grid_hourly/','ERA5_1hr_1979_01_DET.nc')


BC_data = energy_model_functions.meanBC_wind_speed_data(speed100m_data,'/home/users/zd907959/code_folders/S2S4E/wind_power_model/ERA5_model/ERA5_speed100m_mean_factor_v16_hourly.npy')


gridded_wind_power_class1 = energy_model_functions.convert_to_windpower(BC_data,'/home/users/zd907959/code_folders/S2S4E/wind_power_model/Enercon_E70_2300MW_ECEM_turbine.csv')


gridded_wind_power_optimal = energy_model_functions.convert_to_windpower_optimal_turbine(BC_data,'/home/users/zd907959/code_folders/S2S4E/wind_power_model/ERA5_model/ERA5_turbine_array_total_BC_v16_hourly.nc','/home/users/zd907959/code_folders/S2S4E/wind_power_model/Enercon_E70_2300MW_ECEM_turbine.csv','/home/users/zd907959/code_folders/S2S4E/wind_power_model/Gamesa_G87_2000MW_ECEM_turbine.csv','/home/users/zd907959/code_folders/S2S4E/wind_power_model/Vestas_v110_2000MW_ECEM_turbine.csv')



country_wind_power_optimal = energy_model_functions.country_wind_power(gridded_wind_power_optimal,'/home/users/zd907959/code_folders/S2S4E/european_country_masks/ERA5_inst_wp_cap/France_ERA5_windfarm_dist.nc')

country_wind_power_class1 = energy_model_functions.country_wind_power(gridded_wind_power_class1,'/home/users/zd907959/code_folders/S2S4E/european_country_masks/ERA5_inst_wp_cap/France_ERA5_windfarm_dist.nc')


