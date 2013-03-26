Task
----

The goal is to develop new features or build novel tree-like structures to improve the baseline system.

Baseline
--------

**datasets** - contains a folder with raw datasets for training (folder **train/**) and testing (folder **test/**). The golden labels, i.e. true scores are in the folder **gold/**. Please refer to the **00-readme.txt** for a more detailed description.

Running the system
------------------
Compile the SVM binary:

`cd SVM-Light-1.5-rer`

`make`

`cd ..`

Train, test and evaluate:
`sh train-test-eval.sh <sys_name>`

To run a system with the basic features:

`sh train-test-eval.sh baseline`

##Task

* Use raw data from **datasets/** folder to build your own features. 
* Add your features to the baseline features under **models/baseline/** folder
* Put your model with new features under the **models/** folder. Give it a name, i.e. **system1**.
* Evaluate how well you do: 

`sh train-test-eval.sh system1`