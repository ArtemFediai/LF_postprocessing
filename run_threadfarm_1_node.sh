#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=76
#SBATCH --time=0-24:00:00
#SBATCH --mem-per-cpu=2000mb
#SBATCH --job-name=Lightforge
#SBATCH --partition=accelerated # dev_cpuonly 10 min, dev_accelerated, cpuonly, accelerated
##SBATCH --mail-type=ALL
##SBATCH --mail-user=artem.fedyay@gmail.com
#SBATCH --error out_%j.err
#SBATCH --output out_%j.out


export NANOMATCH=/home/hk-project-virtmat/bh5670/QP_installation_V4/nanomatch
export NANOVER=V4
source $NANOMATCH/$NANOVER/configs/lightforge.config

#
export THREADFARMBIN=/home/hk-project-virtmat/bh5670/QP_installation_V4/nanomatch/V4/QuantumPatch/mpithreadfarm/bin
#export PYTHONPATH=$THREADFARM:$PYTHONPATH
#export PATH=$THREADFARM:$PATH
#
export THREADFARM=/home/hk-project-virtmat/bh5670/QP_installation_V4/nanomatch/V4/QuantumPatch/mpithreadfarm
export PYTHONPATH=$THREADFARM:$PYTHONPATH
export PATH=$THREADFARM:$PATH

module load compiler/gnu/11

#$MPI_PATH/bin/mpirun -n 10 --bind-to none --mca btl self,vader,tcp python -m mpi4py  $LFPATH/lightforge.py  -s settings 

cd ${SLURM_SUBMIT_DIR}
ulimit -s unlimited

export KMP_AFFINITY=none

$MPI_PATH/bin/mpirun --bind-to none --mca btl self,vader,tcp python $THREADFARMBIN/thread_mpi_exe.py joblist
#mpirun thread_mpi_exe.py joblist

