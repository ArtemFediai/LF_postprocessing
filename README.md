# Lightforge Postprocessing

---

## Clone the package on the cluster
Assume the home directory is:
```shell
$ HOME=/home/hk-project-virtmat/bh5670
```
Do the following:
```shell
$ cd $HOME
$ git clone https://github.com/ArtemFediai/LF_postprocessing.git
```

##Set the environment for the module LF_postprocessing
Assume requirements.txt yielded nanomatch_scientific environment
(without the name in $HOME/QP_installation_V4/nanomatch/V4/local_anaconda/envs/nanomatch_scientific).
make:
$ conda activate $HOME/QP_installation_V4/nanomatch/V4/local_anaconda/envs/nanomatch_scientific
$ conda develop ~/LF_postprocessing


##Prepare the data for the simulation
e.g.:
$ ws_list
id: lightforge
     workspace directory  : /hkfs/work/workspace/scratch/bh5670-lightforge
     remaining time       : 22 days 5 hours
     creation time        : Mon Nov  8 15:47:51 2021
     expiration date      : Fri Jan  7 15:47:51 2022
     filesystem name      : hkfswork
     available extensions : 3
$ cd  /hkfs/work/workspace/scratch/bh5670-lightforge
$ mkdir 16122021
$ cd 16122021
$ cp ~/LF_postprocessing/CONFIG.yaml .
$ cp ~/LF_postprocessing/settings_dop .

Here, two latter lines were copied as default examples of the CONFIG.yaml and settings_dop (files with the LF hyperparameters and the reference settings file).
You should  change them according to your needs. 

##Generate files to start threadfarm
$ python ~/LF_postprocessing/lf_wrapper.py

Three additional files will be generated:
joblist 
run_lf_from_threadfarm.sh
lf_wrapper.yaml 

The first two are the input file for the threadfarm and the sh file for SLURM, respectively.
The third one is simply the summary of the variable LF parameters (hyperparameters). Intended for a user that will quickly understand what was simulated.
