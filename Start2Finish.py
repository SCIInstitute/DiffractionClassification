from __future__ import print_function
from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import pyFAI
import Image

from mpl_toolkits.mplot3d import Axes3D
from skimage import exposure as ex
from skimage.external import tifffile as tif
from scipy import signal
from scipy.optimize import curve_fit

import hyperspy.api as hs

PIXEL_SIZE = 27.0213 #microns/pixel
CAMERA_DIST = 232.6 #millimeters
WAVELENGTH = .002507921 #nanometers

def Kv2WaveLength(voltage):
    """
    Converts Kv to wavelength
    
    Inputs:

    	voltage in KV
    """

    beamvoltage=voltage*1000
    c=2.998e8
    m=9.1095e-31
    h=6.6261e-34
    e=1.6022e-19

    return h/np.sqrt((2*m*beamvoltage*e*(1+(e*beamvoltage)/(2*m*c**2))))
    

def pixel2theta(x,SIZE=PIXEL_SIZE,DIST=CAMERA_DIST,WAVE=WAVELENGTH):
    r = x*SIZE*1e-3
    d = DIST * WAVE / r
    d = d*10 #nanometer to angstroms
    theta = np.arcsin((WAVE*10)/(2*d))*(360.0/np.pi)*180/np.pi #radians->degrees*2
    
    return theta

def radial_profile(data,center,bins):
	"""
	Creates an azimuthal integration of the image.

	creates rings shifting outwards and sum 
	"""
    y, x = np.indices((data.shape))
    r = np.sqrt((x - center[0])**2 + (y - center[1])**2)
    maximum = np.amax(r)
    target= bins
    r = target*r/maximum
    r = r.astype(np.int)
    
    
    tbin = np.bincount(r.ravel(), data.ravel())
    nr = np.bincount(r.ravel())
    prin(nr,tbin)
    radialprofile = tbin / nr

    return maximum, range(len(radialprofile)),radialprofile 

def plot_signals(signals):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    zs = 0
    for i in range(len(signals)):
        signal = signals[i]
        zs += 1
        ax.plot(signal[0],[zs]*len(signal[0]),np.log(signal[1]))
    ax.view_init(45,280)
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

    ax.xaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    #x.yaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    ax.zaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    ax.w_zaxis.line.set_lw(0.)
    ax.w_yaxis.line.set_lw(0.)
    ax.set_yticks([])
    ax.set_zticks([])

    print(zs)
    plt.show()


def peak_finder(signal,filter_size=3,passes=5):
    size = len(signal)
    possible=0
    
    #signal = np.pad(signal,(filter_size+passes*2,filter_size+passes*2),'constant', constant_values=(0))
    signal = np.pad(signal,(filter_size+passes,filter_size+passes),'constant', constant_values=(0))
    
    votes = np.zeros_like(signal)
    for j in range(passes):
        for i in range(0,size+j):
            scalar = 1
            votes[np.argmax(signal[i:i+filter_size+j])+i] += scalar
        
        votes[votes<np.amax(votes)/2] = 0        
        possible += filter_size+2*j

   #votes[votes<filter_size] = 0
    inner = (filter_size+passes)
    return votes[inner:-inner]

def plot_peaks(sig,votes):
    indicies = np.where(votes>0)
    plt.figure(figsize=(12,4))
    plt.plot(sig)
    sig_min = np.amin(sig)
    for index in indicies[0]:
        x = np.array([index,index])
        y = np.array([sig[index],sig_min])
        plt.plot(x,y)
    plt.show()

def d_to_theta(d,wavelength):
    if type(d) == float or type(d)==int:
        theta_vec = np.arcsin(wavelength/(2*d)) * 180/np.pi()
    elif type(d) == np.darray:
        theta_vec = np.arcsin(wavelength/(2*d)) * 180/np.pi()
    elif type(d) == list:
        theta_vec = np.arcsin(wavelength/(2*np.array(d))) * 180/np.pi()

    else:
        raise ValueError("invalid d-values, must be a single value or list/array of values")

    theta_vec = np.arcsin(wavelength/(2*d)) * 180/np.pi()

    return theta_vec

def norm_reg(image):
    # Regularize by adding 1 to remove zeros
    reg = image + 1

    # Normalize after switching to logscale
    normed = np.log(reg)
    reg_normed = normed/np.amax(normed)
    
    return reg_normed * 10

def process_signal(signal1d,func):
    def func(x):
        return .5*(1.8+(x**3/len(y)**3)*.2)
    
    # find the edges and minima
    #bins = [signal1d[0]]
    #divisions = len(signal1d)//
    x,y = signal1d[0],signal1d[1]
    """
    bins = np.linspace(0,len(y),len(y))
    plt.plot(func(bins))
    plt.show()
    processed_signal = (x,y*func(bins))
    """
    processed_signal = func(signal1d)
    
    return processed_signal


def fit_exponential(processed_signal1d):
    # two term exponential
    def func(x,a,b,c,d):
        x=np.array(x)
        return (a * np.exp(-1*(b*x)) + c* np.exp(-1*(d*x)))
    
    # elucidate x,y
    x = processed_signal1d[0][:-10]
    y = processed_signal1d[1][:-10]

    # fit a curve to the signal
    initial_point = (1.0,1.0,1.0,1.0)
    #try:
    popt, pcov = curve_fit(func,x,y,p0=initial_point)

    # elucidate variables
    v1,v2,v3,v4 = popt[0],popt[1],popt[2],popt[3]
    
    # find residual
    residuals = y - np.array(func(x,float(v1),float(v2),float(v3),float(v4)))
    
    min_residual = np.amin(residuals)
    if min_residual < 0:
        residuals -= min_residual
        residuals += 1
    elif min_residual == 0:
        residuals += 1 
    else:
        residuals += 1
        
        
    
    plt.plot(.75*func(x,v1,v2,v3,v4))
    plt.plot(y)
    plt.show()
    
    #except Exception as e:
    #    print(e)
        # residuals need to be defined a different way
    #    residuals = y
        
    # check if error is sufficient
    # placeholder
    
    return (x,residuals)


"""
Divide the image into sub portions 
"""
def make_chunks(image,divisions_x=4,divisions_y=4):
    chunks = []
    shape = image.shape
    x_div = shape[0]//divisions_x
    y_div = shape[1]//divisions_y
    for x in range(divisions_x):
        for y in range(divisions_y):
            #checking = np.zeros_like(image)
            #checking[x_div*x:x_div*(x+1),y_div*y:y_div*(y+1)] = 100#image[x_div*x:x_div*(x+1),y_div*y:y_div*(y+1)]
            #chunks.append(checking)
            chunks.append(image[x_div*x:x_div*(x+1),y_div*y:y_div*(y+1)])
    return chunks


"""
Azimuthal integration of a diffraction pattern
PIXEL_SIZE = 27.0213 #microns/pixel
CAMERA_DIST = 232.6 #millimeters
WAVELENGTH = .002507921 #nanometers
"""
def azimuthalize(image,detector,ai,pixel_x=.037,pixel_y=.037,z=232.6,bins=128):
    center = np.argmax(image)
    x = int(center%image.shape[0])
    y = int(center/image.shape[0])   
    
    # set the center of the image
    #ai.setFit2D(z,x,y,pixelX=pixel_x,pixelY=pixel_y)
    
    # integrate the image
    #return ai.integrate1d(image,bins,unit='2th_deg')
    return radial_profile(image,(x,y),bins)
    
    
def convert(target,maximum,x):
    new_x = np.linspace(0,maximum,target)
    thetas = pixel2theta(new_x)
    s = target/maximum
    last_x = []
    for i in range(len(x)):
        last_x.append(thetas[int(s*i)])
    return last_x

def save_images(chunks,signals1d,name,folder=os.getcwd()):
    """ Save the images sequentially """

    for i in range(len(chunks)):
        # set the path to save the images
        fname = os.path.join(folder,name +str(i)+ ".tif")

        # save the image
        im = Image.fromarray(chunks[i])
        im.save(fname)
        
    # save the list of 1D signals as a pickle
    sig_name = os.path.join(folder,name + "_integrated" + ".pkl")
    with open(sig_name,'wb') as f:
        pickle.dump(signals1d,f)
