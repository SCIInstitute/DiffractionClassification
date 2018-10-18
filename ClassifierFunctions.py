from matplotlib import pyplot as plt
from future.builtins.misc import input


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

def validate_profile_choice(dims):

    if dims[0] > 1:
        profile_choice = int(input("Multiple profiles detected.\nplease choose which profile to use.\n"))
        while profile_choice not in range(dims[0]):
            profile_choice = int(input("Incorrect selection.\nplease choose {}.\n".format(range(dims[0]))))            
    else:
        profile_choice = 0


    return profile_choice


def set_calibration(is_profile):

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

    print("The data is a profile.")

    if len(image_data.shape) == 1:
        plt.plot(image_data)
        plt.show(block=False)            

    else:
        # show the user which profiles are present
        for i in range(image_data.shape[0]):
            plt.plot(image_data[i,:], label="profile {}".format(i))
        plt.legend()
        plt.show(block=False)

        # have the user select the profile
        profile_choice = cf.validate_profile_choice(image_data.shape)
        plt.close()
        
        image_data = image_data[profile_choice]
        # show chosen profile
        plt.plot(image_data)
        plt.show(block=False)


def choose_display():

    choices = ["d","theta","both"]

    temp_choice = "false"

    while temp_choice not in choices:
        temp_choice = input("Please choose the scale to display.\nd, theta, both\n")
        if temp_choice not in choices:
            print("incorrect choice\n")

    return temp_choice


def choose_peaks(peak_locs,display_type):

    d = peak_locs["d_spacing"]
    theta = peak_locs["2theta"]
    vec = peak_locs["vec"]

    if display_type == "d" or display_type =="both":
        print(d)

    if display_type == "theta" or display_type =="both":
        print(theta)

    maximum = min(len(d),len(theta))

    raw_choices =  input("Choos which peaks you'd like to select separated by spaces.\n").split(" ")

    temp_choices = []

    for choice in raw_choices:
        try:
            temp_index = int(choice)
            if temp_index > 0 and temp_index < maximum-1 and temp_index not in temp_choices:
                temp_choices.append(temp_index)
            else:
                print("index {} outside of available peaks".format(temp_index))
        except:
            print("couldn't convert {} into an index".format(choice))

    print(temp_choices)

    temp_locs = {
                "d_spacing":[d[i] for i in temp_choices],
                "2theta":[theta[i] for i in temp_choices],
                "vec":[vec[i] for i in temp_choices]
                }

    return temp_locs

def provide_family():

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