README.txt

####Welcome to the DeepdiveCrystallography diffraction classification web service

###Quickstart Guide:

prerequisites: python 3.6 and an internet connection

To predict the crystal structure simply start the Diffraction Classifier by
running the command:

python DiffractionClassifier.py

Then follow the series of prompts.

Advanced usage:
	You can specify the data you'd like to load by adding --filepath FILEPATH_TO_YOUR_DATA
	to the function call.

	Similarly you specify the calibration by modifying the calibration.json file and adding --calibration calibration.json to the 
	function call.

### Acknowledgements

Work supported through the INL Laboratory Directed Research& Development (LDRD) Program under DOE Idaho Operations Office Contract DE-AC07-05ID145142. Thanks to Ian Harvey for many useful discussions and contributions to this work.


### Citations

- J. A. Aguiar, M. L. Gong, R. R. Unocic, T. Tasdizen, & B. D. Miller.  Decoding Crystallography from High-Resolution Electron Imaging and Diffraction Datasets with Deep Learning. Sci. Adv. aaw1949 (2019).

- J. A. Aguiar, M. L. Gong & T. Tasdizen. Crystallographic prediction from diffraction and chemistry data for higher throughput classification using machine learning. Comput. Mater. Sci. 173, 109409 (2020).


