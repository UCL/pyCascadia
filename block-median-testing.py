from pygmt import blockmedian
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

filepath = "C:\\Users\\Alessandro\\Documents\\UCL-projects\\bathymetry-sample-data\\gebco_2019.nc"

xr_data = xr.open_dataarray(filepath)

lats = 300
lons = 300

# let's do this in a way where we don't create a super big list!
data = {'x': [], 'y': [], 'z': []}
for lat_index in range(lats):
    for lon_index in range(lons):
        data['x'].append(xr_data.coords['lat'].data[6000-lon_index])
        data['y'].append(xr_data.coords['lon'].data[lat_index])
        data['z'].append(xr_data.data[lat_index, lon_index])

pd_data = pd.DataFrame(data)
region = [min(data['x']), max(data['x']), min(data['y']), max(data['y'])]
bmd = blockmedian(pd_data, spacing=0.05, region=region)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(xs=data['x'], ys=data['y'], zs=data['z'], s=0.1)
ax.scatter(xs=bmd['x'], ys=bmd['y'], zs=bmd['z'])

plt.show()