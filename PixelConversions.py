from __future__ import print_function
from __future__ import division

import matplotlib.pyplot as plt
import numpy as np

import math


"""
Converts Kv to wavelength
#deprecated since this can just fed obtained from calibration
"""
def Kv2WaveLength(voltage):
    """
    Converts Kv to wavelength
    """
    beamvoltage=voltage*1000
    c=2.998e8
    m=9.1095e-31
    h=6.6261e-34
    e=1.6022e-19

    return h/np.sqrt((2*m*beamvoltage*e*(1+(e*beamvoltage)/(2*m*c**2))))

"""

"""
def pixel2theta(x,bin_scale,SIZE,DIST,WAVE):
    """
    Inputs:
        x : vector of bins
        bin_scale: pixels per bin, necessary if bins are a range
        SIZE: pixel_size in microns/pixel
        DIST: distance of camera from sample in millimeters
        WAVE: wave length in nanometers
    """
   
    # Pixels * micron/pixel * millimeters/micron = millimeters
    r = x*bin_scale*SIZE*1e-3 #in millimeters 

    d = DIST * WAVE / r # millimeters * nanometers / millimeters should be nanometers or angstroms

    small_scale = np.average(d)
    
    if small_scale < 1: 
        print("Warning: the Dspacings were suspected to be nanometers and were scaled up to angstroms")
        d = d * 10 # convert from nanometers to angstroms
    

    theta = np.arcsin((1/d))*360/np.pi #radians->degrees*2
    
    return theta, d

def d_to_theta(d,wavelength):
    if type(d) == float or type(d)==int:
        theta_vec = np.arcsin(wavelength/(2*d)) * 180/np.pi()
    elif type(d) == np.ndarray:
        theta_vec = np.arcsin(wavelength/(2*d)) * 180/np.pi()
    elif type(d) == list:
        theta_vec = np.arcsin(wavelength/(2*np.array(d))) * 180/np.pi()

    else:
        raise ValueError("invalid d-values, must be a single value or list/array of values")

    theta_vec = np.arcsin(wavelength/(2*d)) * 180/np.pi()

    return theta_vec

def theta_to_d(theta,wavelength):
    if type(theta) == float or type(type)==int:
        d_vec = np.arcsin(wavelength/(2*theta)) * 180/np.pi()
    elif type(theta) == np.darray:
        d_vec = np.arcsin(wavelength/(2*theta)) * 180/np.pi()
    elif type(d) == list:
        d_vec = np.arcsin(wavelength/(2*np.array(theta))) * 180/np.pi()

    else:
        raise ValueError("invalid d-values, must be a single value or list/array of values")

    #d_vec = np.arcsin(wavelength/(2*theta)) * 180/np.pi()

    return d_vec


def norm_reg(image):
    # Regularize by adding 1 to remove zeros
    reg = image + 1

    # Normalize after switching to logscale
    normed = np.log(reg)
    reg_normed = normed/np.amax(normed)
    
    return reg_normed #* 10

