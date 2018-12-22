import csv
import os
import numpy as np 

from matplotlib import pyplot as plt
from future.builtins.misc import input


def validate_calibration(prompt,name):
    """
    ensures proper options are chosen for calibration    
    """
    
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

def validate_profile_choice(dims):
    """
    ensure proper options are chosen for selecting a single profile 

    """

    if dims[0] > 1:
        profile_choice = int(input("Multiple profiles detected.\nplease choose which profile to use.\n"))
        while profile_choice not in range(dims[0]):
            profile_choice = int(input("Incorrect selection.\nplease choose {}.\n".format(range(dims[0]))))            
    else:
        profile_choice = 0


    return profile_choice


def set_calibration(is_profile):
    """
    prompt user to fill in proper calibration parameters
    """


    print("No calibration could be extracted from the file metadata\n Please enter calibration paramters")
    
    pixel_size = validate_calibration("Please enter a pixel size (in angstroms) e.g. 14.1\n","pixel_size")
    
    wavelength = validate_calibration("Please enter beam wavelength (in microns) e.g. .02354\n","wavelength")            

    if not is_profile:     
        camera_dist = validate_calibration("Please enter camera distance from sample (in millimeters) e.g. 223.1\n","camera distance")
    else:
        camera_dist = 0

    return { "pixel_size":   pixel_size,
            "wavelength":   wavelength,
            "camera_distance":  camera_dist}

def choose_profile(image_data):
    """
    prompts user to select a profile if multiple are detected
    """
    print("The data is a profile.")

    if len(image_data.shape) == 1:
    
        plt.plot(image_data)
        plt.show(block=False)

        return image_data,np.array(range(image_data.shape[0]))
    
    elif len(image_data.shape) == 2:
        if image_data.shape[0] == 1:
            plt.plot(image_data[0,:])
            plt.show(block=False)
            #plt.show()

            return image_data[0,:],np.array(range(image_data.shape[1]))


        elif image_data.shape[1] == 1:
            plt.plot(image_data[1,:])
            plt.show(block=False)
            #plt.show()
            return image_data[0,:],np.array(range(image_data.shape[1]))



        else:
            ""

            return image_data[1,:],image_data[0,:]

    else:
        # show the user which profiles are present
        for i in range(image_data.shape[0]):
            plt.plot(image_data[i,:], label="profile {}".format(i))
        plt.legend()
        plt.show(block=False)

        # have the user select the profile
        profile_choice = validate_profile_choice(image_data.shape)
        plt.close()
        
        image_data = image_data[profile_choice]
        
        # show chosen profile
        plt.plot(image_data)
        plt.show(block=False)
        
        return image_data

def choose_display():
    """
    prompt user to choose scale bar display
    """

    choices = ["d","theta","both"]

    temp_choice = "false"

    while temp_choice not in choices:
        temp_choice = input("Please choose the scale to display.\nd, theta, both\n")
        if temp_choice not in choices:
            print("incorrect choice\n")

    return temp_choice


def choose_peaks(peak_locs,display_type):
    """
    prompt user to select which peaks to classify on
    """
    d = peak_locs["d_spacing"]
    theta = peak_locs["2theta"]
    vec = peak_locs["vec"]

    if display_type == "d" or display_type =="both":
        print(d)

    if display_type == "theta" or display_type =="both":
        print(theta)

    maximum = min(len(d),len(theta))
    print(maximum,len(d),len(theta))
    raw_choices =  input("Choose which peaks you'd like to select separated by spaces.\n").split(" ")

    temp_choices = []

    for choice in raw_choices:
        try:
            temp_index = int(choice)
            if temp_index > 0 and temp_index <= maximum and temp_index not in temp_choices:
                temp_choices.append(temp_index)
            else:
                print("index {} outside of available peaks".format(temp_index))
        except:
            print("couldn't convert {} into an index".format(choice))

    print(temp_choices)

    temp_locs = {
                "d_spacing":[d[i-1] for i in temp_choices],
                "2theta":[theta[i-1] for i in temp_choices],
                "vec":[vec[i-1] for i in temp_choices]
                }

    return temp_locs

def provide_family():
    """
    prompt user and ensure proper selection of base Crystal family
    """

    family = None

    while family is None:
        temp_choice = input("Would you like to suggest a crystal family? yes or no\n")

        if temp_choice =="yes":
            family = temp_choice
        elif temp_choice =="no":
            family = temp_choice
        else:
            print("Invalid choice. Please choose yes or no\n")

    return family


def write_to_csv(path,data_dict):
    """
    save new row of results to csv
    """


    schema = ["file_name","family","genus","genus_confidence",
            "species_1","confidence_1","hall_1",
            "species_2","confidence_2","hall_2",
            "species_3","confidence_3","hall_3",
            "species_4","confidence_4","hall_4","peaks"]

    # if no file exists create a one and inform the user
    if not os.path.exists(path):
        print("creating new output file {}".format(path))
        with open(path, "wb") as csv_file:
            filewriter = csv.writer(csv_file, delimiter=",")
            filewriter.writerow(schema)

    row = []

    row.append(data_dict["file_name"])
    row.append(data_dict["family"])
    
    row.append(data_dict["genus_1"])
    row.append(data_dict["genus_confidence_1"][:5])
    
    row.append(data_dict["species_1"])
    row.append(data_dict["confidence_1"][:5])
    row.append(data_dict["hall_1"])
    
    row.append(data_dict["species_2"])
    row.append(data_dict["confidence_2"][:5])
    row.append(data_dict["hall_2"])

    row.append(data_dict["species_3"])
    row.append(data_dict["confidence_3"][:5])
    row.append(data_dict["hall_3"])

    row.append(data_dict["species_4"])
    row.append(data_dict["confidence_4"][:5])
    row.append(data_dict["hall_4"])

    row.append(data_dict["peaks"])

    with open(path, "ab") as csv_file:
        filewriter = csv.writer(csv_file, delimiter=",")
        filewriter.writerow(row)



