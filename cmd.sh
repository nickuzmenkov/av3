#!/bin/sh
HOURS_COUNT=[hours]
MINUTS_TO_STOP=0
NODES_COUNT=1
OUTFILE=`mktemp -u .out.XXXXXXX`
rm -f $OUTFILE
if [ ! -n "$1" ]
then
	while [ 1 ]; do
		export PRESET="good"
	    sbatch -p [partition] -t $(($HOURS_COUNT*60)) -N $NODES_COUNT $0 run 2>&1 | tee $OUTFILE
	    grep -q "Batch job submission failed" $OUTFILE || break
	    rm -f $OUTFILE
		exit 0
	done
	rm -f $OUTFILE
	exit 0
fi
[ -z "$SLURM_JOB_NODELIST" ] && exit 1
SLURMCPUNODE="`echo $SLURM_JOB_CPUS_PER_NODE | sed 's/(x[0-9]\+)$//'`"
JCPUNODE=32
MYHOSTFILE="hostfile.$SLURM_JOBID"
rm -f $MYHOSTFILE
touch $MYHOSTFILE
MYHOSTFILE2="hostfile2.$SLURM_JOBID"
MYHOSTFILE3="hostfile3.$SLURM_JOBID"
MYHOSTFILE4="hostfile4.$SLURM_JOBID"
rm -f $MYHOSTFILE2
touch $MYHOSTFILE2
NODELIST=""
RES=`expr index $SLURM_JOB_NODELIST "[,"`
if [ $RES -ne 0 ]; then
    for e in `echo $SLURM_JOB_NODELIST | sed 's/,\([^0-9]\)/ \1/g'`; do
	RES=`expr index $e "["`
	if [ $RES -ne 0 ]; then
	    NBASE="`echo $e | sed 's/^\(.*\)\[.*$/\1/'`"
	    NLIST="`echo $e | sed 's/^.*\[\(.\+\)\]$/\1/;s/,/ /g'`"
	    for i in $NLIST; do
		RES=`expr index $i "-"`
		if [ $RES -ne 0 ]; then
		    x="`echo $i | cut -d- -f1`"
		    y="`echo $i | cut -d- -f2`"
		    for n in `seq -w $x $y`; do
			[ -z "$NODELIST" ] || NODELIST=$NODELIST","
			NODELIST=$NBASE$n:$JCPUNODE
echo $NODELIST >> $MYHOSTFILE
for ii in $(seq 1 1 $JCPUNODE)
do
   echo $NBASE$n >> $MYHOSTFILE2
done
		    done
		else
		    [ -z "$NODELIST" ] || NODELIST=$NODELIST","
		    NODELIST=$NBASE$i:$JCPUNODE
echo $NODELIST >> $MYHOSTFILE
for ii in $(seq 1 1 $JCPUNODE)
do
   echo $NBASE$i >> $MYHOSTFILE2
done
		fi
	    done
	else
	    [ -z "$NODELIST" ] || NODELIST=$NODELIST","
	    NODELIST=$e:$JCPUNODE
echo $NODELIST >> $MYHOSTFILE
for ii in $(seq 1 1 $JCPUNODE)
do
   echo $e >> $MYHOSTFILE2
done
	fi
    done
else
	NODELIST=$SLURM_JOB_NODELIST:$JCPUNODE
echo $NODELIST >> $MYHOSTFILE
for ii in $(seq 1 1 $JCPUNODE)
do
   echo $SLURM_JOB_NODELIST >> $MYHOSTFILE2
done
fi
cat $MYHOSTFILE2 | sed s/node0/node/ > tmp.txt
cat tmp.txt > $MYHOSTFILE2
cat $MYHOSTFILE | sed s/node0/node/ > tmp.txt
cat tmp.txt > $MYHOSTFILE
rm -fr tmp.txt
NCPU=$(($NODES_COUNT*$JCPUNODE))
echo "free:"
free
echo "ulimit -a:"
ulimit -a
echo "start job"
stat /aviator3/ansys_inc/shared_files/licensing/linx64/ansysli_client
echo #
if [ "$MINUTS_TO_STOP" -ne "0" ]; then
    sleep $(($HOURS_COUNT*60*60-$MINUTS_TO_STOP*60)) && echo "save" > $MODEL.MOD && echo "save" >> test.txt && echo "STOP COMMAND SENDED" &
fi
echo #
export PBS_NODEFILE=$MYHOSTFILE4
sed -e 's/node0/node/g' $MYHOSTFILE2 > $MYHOSTFILE3
sed -e 's/node0/node/g' $MYHOSTFILE3 > $MYHOSTFILE4
unset DISPLAY
module available
module unload compilers/intel/2017.4.196 mpi/intel/2017.4.196
module unload compilers/intel/2018.0.128 mpi/intel/2018.0.128
. /aviator3/ansys_inc/v182/bashrc
export I_MPI_FABRICS=shm:ofi:dapl:ofa
export I_MPI_DEBUG=6
export I_MPI_FALLBACK=1
module list
ls -Al /dev/infiniband/
echo "=" > log_job.$SLURM_JOBID.txt
echo $HOSTNAME >> log_job.$SLURM_JOBID.txt
echo "start" >> log_job.$SLURM_JOBID.txt
echo "job CMD=$CMD" >> log_job.$SLURM_JOBID.txt
echo "start :" `date` >> log_job.$SLURM_JOBID.txt
eval export > export.$SLURM_JOBID.txt
echo =
cat $PBS_NODEFILE
echo =
$ANSYS_HOME/v182/fluent/bin/fluent [dim]d -g -t[cpus] -pib -mpi=intel "-cnf=$PBS_NODEFILE" -i "cmd.jou"
[postscript]
echo "stop  :" `date` >> log_job.$SLURM_JOBID.txt
echo #
sync
rm -f $LOCK_FILE
echo ">>> host $THIS_HOST: Exiting..."
