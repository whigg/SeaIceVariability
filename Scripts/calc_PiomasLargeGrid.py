"""
Scripts creates plots of large grid cells (nxn) for different statistical
variables. 

Author : Zachary Labe
Date : 13 September 2016
"""

### Import modules
import numpy as np
from netCDF4 import Dataset
import scipy.stats as sts
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import datetime
import iris as ir
import iris.quickplot as qplt

### Define directories
directorydata = '/home/zlabe/Surtsey/seaice_obs/PIOMAS/Thickness/'  
directoryfigure = '/home/zlabe/Desktop/'

### Define time           
now = datetime.datetime.now()
currentmn = str(now.month)
currentdy = str(now.day)
currentyr = str(now.year)
currenttime = currentmn + '_' + currentdy + '_' + currentyr
titletime = currentmn + '/' + currentdy + '/' + currentyr
print '\n' '----Calculate PIOMAS large grid cells - %s----' % titletime 

### Alott time series
yearmin = 1979
yearmax = 2015
years = np.arange(yearmin,yearmax+1,1)

### Read in 100km EASE Piomas regridded
data = Dataset(directorydata + 'piomas_regrid_sit_19792015.nc')
lats = data.variables['lat'][:]
lons = data.variables['lon'][:]
sit = data.variables['newthickness'][:]
data.close()

sit[np.where(sit < 0.01)] = np.nan

print 'Completed: Read PIOMAS data!'

def transformGrid(var,la,lo):
    """
    Creates new grid with filled cells for averaged thickness
    over set bounds.
    """
    var = np.nanmean(var,axis=1)

    varn_re = np.empty(var.shape)
    for i in xrange(var.shape[0]):
        for j in xrange(0,var.shape[1]-la,la):
            for k in xrange(0,var.shape[2]-lo,lo):
                averaging = np.nanmean(var[i,j:j+la,k:k+lo])
                varn_re[i,j:j+la,k:k+lo] = averaging
                
    print 'Completed: Grid transformation!'                   
    return varn_re

la = 1
lo = 1

sitq = transformGrid(sit,la,lo)
sitq[np.where(sitq < 0.05)] = np.nan

slopesit = np.zeros((sitq.shape[1],sitq.shape[2]))
for i in xrange(0,sitq.shape[1]-la,la):
    for j in xrange(0,sitq.shape[2]-lo,lo):
        varyy = np.ravel(sitq[:,i,j])
        varxx = np.arange(varyy.shape[0])
        mask = np.isfinite(varxx) & np.isfinite(varyy)
        
        varyymean = np.nanmean(varyy)
        if np.isfinite(varyymean):
            slopesit[i:i+la,j:j+lo],intercept,r,p_value,std_err = sts.stats.linregress(varxx[mask],
                                                              varyy[mask])
        else:
            slopesit[i:i+la,j:j+lo] = np.nan                                         
print 'Completed: Script done!'

slopesit = slopesit*10.

### Call parameters
plt.rcParams['text.usetex']=True
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Avant Garde'

### Define figure
fig = plt.figure()
ax = plt.subplot(111)

m = Basemap(projection='npstere',boundinglat=66,lon_0=270,resolution='l',round =True)    
m.drawmapboundary(fill_color='white')
m.drawcoastlines(color='k',linewidth=0.5)
parallels = np.arange(50,90,10)
meridians = np.arange(-180,180,30)
m.drawparallels(parallels,labels=[False,False,False,False],
                linewidth=0.5,color='k',fontsize=9)
m.drawmeridians(meridians,labels=[True,True,False,False],
                linewidth=0.5,color='k',fontsize=9)
m.drawlsmask(land_color='darkgrey',ocean_color='mintcream')

### Adjust maximum limits
values = np.arange(-1,1.1,0.1)  

### Plot filled contours    
cs = m.contourf(lons[:,:],lats[:,:],slopesit[:,:],
                values,latlon=True,extend='both')
                  
### Set colormap     
#cmap = plt.cm.get_cmap('brewer_RdBu_11')      
cmap = plt.cm.get_cmap('seismic_r')                      
cs.set_cmap(cmap)
                          
cbar = m.colorbar(cs,location='right',pad='10%',
                    extend='both',extendfrac=0.07,drawedges=True)

cbar.set_label(r'decadal trend (m)')
cbar.set_ticks(np.arange(-1,1.1,0.25))
cbar.set_ticklabels(map(str,np.arange(-1,1.1,0.25))) 
#cbar.tick_params(axis=u'both', which=u'both',length=0)

fig.subplots_adjust(bottom=0.15)

### Save figure
plt.savefig(directoryfigure +'largegrid2.png',dpi=500)        
        