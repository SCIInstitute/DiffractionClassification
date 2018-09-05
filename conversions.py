import numpy as np


"""
convert between d-spacing and two theta
"""

def d_to_theta(d,wavelength):
    """
    """

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



def theta_to_d(theta,wavelength):


    if type(theta) == float or type(theta)==int or type(theta) == np.darray:
        d_vec = wavelength/(np.sin(theta)*2)
    elif type(theta) == list:
        d_vec = wavelength/(np.sin(np.array(theta*np.pi/180))*2)
    else:
    	raise ValueError("invalid theta-values, must be a single value or list/array of values")



    return d_vec


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


def pixel2theta(x,SIZE=PIXEL_SIZE,DIST=CAMERA_DIST,WAVE=WAVELENGTH):
    r = x*SIZE*1e-3
    d = DIST * WAVE / r
    d = d*10 #nanometer to angstroms
    theta = np.arcsin((WAVE*10)/(2*d))*(360.0/np.pi)*180/np.pi #radians->degrees*2

    return theta


def inverseNM2angstroms(invert):
    return 10.0/invert