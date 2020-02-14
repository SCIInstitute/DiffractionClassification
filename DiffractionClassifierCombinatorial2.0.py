import ClientSide2 #custom package

import numpy as np
import argparse
import json
import os
import ClassifierFunctions2 as cf

from matplotlib import pyplot as plt
from builtins import input

from Notation import SpaceGroupsDict as spgs
SpGr = spgs.spacegroups()



from itertools import combinations,chain


# Initialize essential global variables
#URL =  "" #you'll need me to send you the link
FAMILIES = ["triclinic","monoclinic","orthorhombic","tetragonal",
        "trigonal","hexagonal","cubic"]

DEFAULT_SESSION = os.path.join ("Sessions","session.json")
DEFAULT_USER = "user_profile.json"
SERVER_INFO = "server_gen2.json"

# list of three, one per level
prediction_per_level = [1, 1, 2]
num_peaks = [7, 10]


def build_parser():
    parser = argparse.ArgumentParser()

    # This will be implemented as rollout broadens
    parser.add_argument('--apikey', type=str,
                        dest='key', help='api key to securely access service',
                        metavar='KEY', required=False)

    parser.add_argument('--session',
                        dest='session', help='Keep user preferences for multirun sessions', metavar='SESSION',required=False, default=None)
    parser.add_argument('--subset',
                        dest='subset',help='Run a small number of the possible combinations.  Mostly for testing. Input the number of combos to run.', metavar='NO_OF_COMBOS',required=False, default=None)
    parser.add_argument('--dataonly',
                        dest='data_only',help='run the classification without plotting', metavar='True/[False]',required=False, default=False)
    parser.add_argument('--figuresonly',
                        dest='figures_only',help='Plot the figures without running data.  Data must be saved previously.', metavar='True/[False]',required=False, default=False)
    
    return parser

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))



def combination_peaks(peak_batch, chem_vec, mode, temp_name, crystal_family, user_info, URL, prediction_per_level, subset, num_peaks):

    outpath = "Ready"
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    find_valid_peaks = list(powerset(peak_batch["vec"]))
    find_valid_peaks = [item for item in find_valid_peaks if len(item) > num_peaks[0] and len(item) < num_peaks[1]]
    print(len(find_valid_peaks),"valid peak combinations")

    valid_peaks_combinations = [{"vec":proto_combo} for proto_combo in find_valid_peaks]
    found = False
    threshold = 0
    tot_spec = 1
    for p in prediction_per_level:
        tot_spec *= p
    guesses = {}
    for k in range(1,tot_spec+1):
        guesses["species_"+str(k)]=[]
        guesses["spec_confidence_"+str(k)]=[]
#    print(guesses)
    common_peaks = []
    failed_combos = valid_peaks_combinations
    #peak_locs,user_info,URL,fam
    persistance = 0
    LIMIT = 3
#    print(failed_combos)
    while len(failed_combos) > 0 and persistance < LIMIT:
        for combo in failed_combos[0:subset]:
            try:
#                print('---classifying---')
#                print(combo)
                classificated = ClientSide2.Send_For_Classification(combo, chem_vec, mode, crystal_family, user_info, URL, prediction_per_level)
                print(classificated)
                classificated["file_name"] = temp_name
    #                print('name =')
    #                print(temp_name)
                print(os.path.join(outpath,temp_name))
                cf.write_to_csv(os.path.join(outpath,temp_name) + ".csv", classificated, prediction_per_level)
                print(tot_spec)
                for k in range(1,tot_spec+1):
                    print(guesses)
                    guesses['species_'+str(k)].append( classificated["species_"+str(k)] )
                    guesses['spec_confidence_'+str(k)].append( classificated["spec_confidence_"+str(k)] )
                    common_peaks.append(classificated["peaks"])
                    
                    
                
                # remove the classified combination
                failed_combos.remove(combo)
                
            except KeyboardInterrupt:
                raise
            except:
                print("An error occured this combination was not classified.\nIt will be retried {} more times".format(LIMIT-persistance))

        persistance += 1

    if len(failed_combos)>0:
        print("there were {} failed combinations".format(len(failed_combos)))
    print('returning')
    return common_peaks, guesses

def make_figures(guesses,crystal_family,froot):

    if crystal_family:
        lower_gen = SpGr.edges["genus"][crystal_family][0]
        upper_gen = SpGr.edges["genus"][crystal_family][1]
    else:
        lower_gen = SpGr.edges["genus"][FAMILIES[0]][0]
        upper_gen = SpGr.edges["genus"][FAMILIES[-1]][1]
    fam_range = range(SpGr.edges["species"][lower_gen][0],1+SpGr.edges["species"][upper_gen][1])
        
    #        phi = 2*np.pi/360
    fig_ang = 300
    phi = (2*np.pi*fig_ang/360)/(max(fam_range)-min(fam_range)+1)
    thet = fig_ang/(max(fam_range)-min(fam_range)+1)
    fam_axes = [1,3,16,75,143,168,195]

    #        fig1 = plt.figure(1,figsize=(len(fam_range),16))
    fig1 = plt.figure(2,figsize=(16,8))
    plt.clf()
    ax1 = fig1.add_axes([0.03,0.1,.96,.8])
#        ax1.set_yscale('log')
    fam_color = ['k','g','b','c','m','y','k']
    for k in range(len(fam_axes)-1):
        ax1.axvspan(fam_axes[k]-0.5,fam_axes[k+1]-0.5,facecolor = fam_color[k], alpha=0.5)
    #        ax1.axvspan(fam_axes[0],fam_axes[1]-1,alpha=0.5)

    ax1.axvspan(fam_axes[-1]-0.5,np.max(fam_range)-0.5,alpha=0.3)
    plt.ion

    fig2 = plt.figure(3,figsize=(8,8))
    plt.clf()
    plt.ion
    ax2 = fig2.add_axes([0.1,0.1,0.8,0.8],polar=True)
    ax2.set_thetamin(1)
    ax2.set_rmin(0)
    ax2.set_thetamax(fig_ang)
    ax2.set_rlabel_position(30)
    ax2.set_theta_direction(-1)
    ax2.set_theta_zero_location("S",offset=-(360-fig_ang)/2)
    #        ax2.set_rscale('log')
    prev_histograms_1 = []
    prev_histograms_2 = []
    plots_1 = []
    plots_2 = []
    print('guesses = ')
    print(guesses)
    num_pred = np.prod(prediction_per_level)
    for rank in range(1,num_pred+1):
        histo = np.histogram([g for g in guesses["species_{}".format(rank)]], weights = [g for g in guesses["spec_confidence_{}".format(rank)]], bins = np.arange(min(fam_range)-0.5, max(fam_range)+1.5))
        histo_log = np.array([np.log10(float(h))+1 if h>0 else 0 for h in histo[0]])
#        print('log_histo = ')
#        print(histo_log.tolist())
        if rank > 1:
            plt.figure(2)
            plot_1 = plt.bar(histo[1][:-1], histo[0], bottom = np.sum(np.vstack(prev_histograms_1), axis=0), align="center", width = 1.1)
            plt.figure(3)
            sum_hist = np.sum(np.vstack(prev_histograms_1), axis=0)
            log_sum = np.array([np.log10(float(h))-1 if h>0 else -1 for h in sum_hist])
#            print('log_sum = ')
#            print(log_sum.tolist())
            plot_2 = plt.bar(histo[1][:-1]*phi, histo_log, bottom = log_sum, align="center", width = phi)
        else:
            plt.figure(2)
            plot_1 = plt.bar(histo[1][:-1], histo[0], align="center", color='red', width = 1.1)
            plt.figure(3)
            plot_2 = plt.bar(histo[1][:-1]*phi, histo_log, bottom = -1, align="center", color='red', width = phi)
            
        plots_1.append(plot_1)
        plots_2.append(plot_2)
        plt.figure(2)
        plt.yticks(rotation='vertical')
        plt.xticks(histo[1][:-1],rotation='vertical')
        prev_histograms_1.append(histo[0])
        prev_histograms_2.append(histo[0])
    #            plt.figure(3)
    #            ax2.set_xticks(histo[1][:-1])

    plt.figure(2)
    #        ym = ax1.get_ymax()*.9

    r_max = 0
    for rect in plot_1:
        n_max = rect.get_height()+rect.get_y()
        if n_max>r_max:
            r_max = n_max
            

    for k in range(len(FAMILIES)-1):
        if k ==0:
            ym_t = r_max*0.7
            cent = 'left'
        else:
            ym_t = r_max*0.6
            cent = 'center'
        ax1.text((fam_axes[k+1]+fam_axes[k])/2,ym_t, FAMILIES[k],  horizontalalignment=cent)


    ax1.text((fam_axes[-1]+np.max(fam_range))/2,ym_t, FAMILIES[-1],  horizontalalignment='center')
        
    ax1.autoscale(enable=True, axis='x', tight=True)
    ax1.tick_params(axis='x', which='major', labelsize=6)
    plt.xlabel("Prediction",fontsize=10)
    plt.ylabel("Counts",fontsize=10)
    #        plt.legend(plots,("species_1","species_2","species_3","species_4"))
    leg_list = [ "species_{}".format(k+1) for k in range(num_pred) ]
    plt.legend(plots_1,leg_list)
    print("Results/"+froot+"_gen2.png")
    plt.savefig("Results/"+froot+"_gen2.png",dpi = 300)

    plt.figure(3)
    #        plt.xlabel("Prediction",fontsize=10,rotation='vertical')
    #        plt.ylabel("Counts",fontsize=10)
    r_ticks = list(range(int(np.floor(ax2.get_rmin())),int(np.ceil(ax2.get_rmax())+1)))
    ax2.set_rgrids(r_ticks, labels = ['10e'+str(r) for r in r_ticks])
    ax2.set_thetagrids([f*thet for f in fam_axes],labels = FAMILIES)
    plt.legend(plots_2,leg_list)
    #        plt.legend(plots,("species_1","species_2","species_3","species_4"))
    print("Results/"+froot+"_gen2_polar.png")
    plt.savefig("Results/"+froot+"_gen2_polar.png",dpi = 300)
#    plt.show()
    

def main():

    parser = build_parser()
    options = parser.parse_args()
    
    if options.subset:
        subset = int(options.subset)
    else:
        subset = -1
        

    print(options.session)

    # opens the user specified session
    if options.session:
        with open(os.path.join("Sessions",options.session),'r') as f:
            session = json.load(f)

    # opens the default session    
    else:
        with open(DEFAULT_SESSION,'r') as f:
            session = json.load(f)

    # set variables from loaded session data
#    print(session)
    file_path = session["file_path"]
    if "output_file" in session:
        output_file = session["output_file"]
    else:
        output_file = ''
    if "output_file_root" in session:
        output_file_root = session["output_file_root"]
    else:
        output_file_root = ''
    if not (output_file or output_file_root):
        raise ValueError('output_file or output_file_root must be defined in session file.')
    manual_peak_selection = session["manual_peak_selection"]
    known_family = session["known_family"]
    chemistry = session["chemistry"]
    diffraction = session["diffraction"]
    
    print('file inputs')
    print(output_file)
    print(output_file_root)
    
    mode = ""
    
    if diffraction:
        if chemistry:
            mode="DiffChem"
        else:
            mode="DiffOnly"
    else:
        if chemistry:
            raise ValueError('Running chemistry only predictions is currently not implemented')
        else:
            raise ValueError('Invalid prediction type. Either diffraction or chemistry must be enabled')

    if known_family and known_family=='yes':
        print('known family')
        crystal_family = session["crystal_family"]
        prediction_per_level[0] = 1
    else:
        crystal_family = None
    
    # Load user from provided path, [IN PROGRESS]
    if session["user_info"]:
        with open(session["user_info"],'r') as f:
            user_info = json.load(f)
    else:
        with open(DEFAULT_USER,'r') as f:
            user_info = json.load(f)
    
    with open(session["server_info"],'r') as f:
        server_info = json.load(f)
        
    if server_info['URL']:
        url = server_info['URL']
    else:
        raise ValueError('you need to have the server URL provided to you')
    
    chem_vec = cf.check_for_chemistry(session)
        
    print(file_path)
    print('---starting loop--')
    # Determine if the path is a directory or a file
    if os.path.isdir(file_path):
        print("loading files from directory")
        file_paths = []
        for dirpath,dirnames,fpath in os.walk(file_path):
            for path in fpath:
                file_paths.append(os.path.join(dirpath,path))
        print("found {} files to load.".format(len(file_paths)))

    else:
        file_paths = [file_path]
        
    if not os.path.exists("Results"):
        os.makedirs("Results")
    

    print(file_paths)
    for f_path in file_paths:

        # Load Data from specified file (DM3, TIFF, CSV etc....)
        
        print("loading data from {}".format(f_path))
        image_data,scale = ClientSide2.Load_Profile(f_path)
        print("I successfully loaded the data")
        
#        print(scale)

        print(options.figures_only)
        print(options.data_only)
        
        # difining filepaths here to facilitate loading data.
        froot = os.path.splitext(os.path.basename(f_path))[0]
        if output_file_root:
            outfile = 'Results/'+output_file_root+froot+'.json'
            outfile_2 = 'Results/'+output_file_root+froot+'_peaks.json'
        else:
            output_file_root='' #for the figure filenames
            [outroot, ext] = os.path.splitext(output_file)
            if not ext=='.json':
                output_file = outroot+'.json'
                output_fil_2e = outroot+'_peaks.json'
            outfile = 'Results/'+output_file
            outfile_2 = 'Results/'+output_file_2

        # optional skipping the data creation
        if options.figures_only:
            print('Only creating figures')
            with open(outfile, 'r') as fp:
                guesses = json.load(fp)
        else:
            if diffraction:
                peak_locs,peaks_h = ClientSide2.Find_Peaks(image_data,scale,25)
                # Choose which peaks to classify on
                if manual_peak_selection:
                    peak_locs = cf.choose_peaks(peak_locs,peaks_h)
                    #raise NotImplementedError
            else:
                peak_locs = []
                peaks_h = []

            
            # Script hangs when there are too many peaks.
            # TODO: implement something better. 
            if len(peak_locs['d_spacing'])>25:
                print("\n\n======================================================")
                print("there are "+ str(len(peak_locs['d_spacing']))+" peaks, which is too many.")
                print(f_path)
                print("======================================================\n\n")
                continue

            
            
            common_peaks,guesses = combination_peaks(peak_locs, chem_vec, mode, froot, crystal_family, user_info, url, prediction_per_level, subset, num_peaks)
        
            # save data
            with open(outfile, 'w') as fp:
                json.dump(guesses, fp)
            with open(outfile_2, 'w') as fp:
                json.dump(common_peaks, fp)
        
        
        if options.data_only:
            print('skipping figures')
        else:
            make_figures(guesses,crystal_family,output_file_root+froot)
        # TODO: Split up this function and enable plotting on precomupted data.
        
        
        #        plt.show(block=False)
        

if __name__ == "__main__":
    main()


