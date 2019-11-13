#!/bin/bash

if [ $# -lt 2 ] ; then
    echo "Usage: $0 param_config_file log_file "
    exit 1
fi 

#Run multiple workers in parallel
param_config_file=$1
log_file=$2

#clear the log_file
echo ' ' > $log_file


n_workers=0
max_loop_step=0

params=''
while IFS=":" read key data
do
    echo "${key} : ${data}"
    if [[ ${key} == 'n_workers' ]]; then
        n_workers=${data}
    fi
    if [[ ${key} == 'max_loop_step' ]]; then
        max_loop_step=${data}
    fi
    a="--${key}=${data} "
    params=$params$a 
done < $param_config_file

echo "---all params: $params"
echo "n_workers: $n_workers"
echo "max_loop_step: $max_loop_step"

visible_gpus="$CUDA_VISIBLE_DEVICES"
IFS=',' read -r -a ARR <<< "$visible_gpus"
cnt=${#ARR[@]}
if [[ $cnt == 0 ]] ; then 
    cnt=$((cnt+1))
fi
echo "cnt == $cnt"
#${ARR[0]}, ${ARR[1]}

play_games() {
    echo -e "play games: $1 processes in parallel"
    hname=`hostname`
    N=$1
    for((i=0; i<$N; i++))
    do
        SEED=$(($RANDOM))
        k=$((i%cnt))
        python pommerman/agents/worker.py ${params} --device_string="cuda:$k" 2>&1 >>$log_file  &
    done
    wait 
}
    

for ((ite=0; ite<$max_loop_step; ite++)) do
    echo "iteration $ite"
    play_games $n_workers
    
    wait
    echo "finished working, optimize nn"
    python pommerman/agents/optimize_nn.py ${params} --iteration=$ite 2>&1 >>$log_file
    
    wait
done

echo "Done"
