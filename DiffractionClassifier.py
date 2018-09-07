import ClientSide #custom package
import argparse

from future.builtins.misc import input
import os


# TESTING IMPORTS
import numpy as np
from matplotlib import pyplot as plt


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', type=str,
                        dest='fpath', help='path to the image',
                        metavar='FPATH', required=True)

    parser.add_argument('--apikey', type=str,
                        dest='key', help='apikey to securely access service',
                        metavar='KEY', required=False)

    return parser

def validate_calibration(prompt,name):
    while True:
        temp_value = input(prompt)
        try:
            float(temp_value)

            if temp_value > 0:
                return float(temp_value)
            else:
                print("invalid {}".format(name))
        except:
            print("invalid {}".format(name))



def main():
    parser = build_parser()
    options = parser.parse_args()

    print("loading data from {}".format(options.fpath))    
    image_data, calibration = ClientSide.Load_Image(options.fpath)
    calibration = None #placeholder for future implementations
    

    print(np.amax(image_data),np.min(image_data))
    # prompt user to provide calibration if none was found
    if calibration is None:
        print("No calibration would be extracted from the file metadata")
        
        pixel_size = validate_calibration("Please enter a pixel size (in angstroms) e.g. 14.1\n","pixel_size")
        camera_dist = validate_calibration("Please enter camera distance from sample (in millimeters) e.g. 223.1\n","camera distance")
        wavelength = validate_calibration("Please enter beam wavelength (in microns) e.g. .02354\n","wavelength")            

        calibration = { "pixel_size":   pixel_size,
                "wavelength":   wavelength,
                "camera_distance":  camera_dist}


    radial_profile = ClientSide.Extract_Profile(image_data)    

    plt.imshow(np.log(image_data))
    plt.show()

    #print(radial_profile[0])
    peak_locs = ClientSide.Find_Peaks(radial_profile,calibration)

    print(peak_locs)


if __name__ == "__main__":
    main()


