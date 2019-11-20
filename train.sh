#!/bin/bash
#
#This script generates a number of games/playouts/rollouts using worker.py and then trains a neural network on those games using optimize_nn.py.
#Playouts are stored in game_dir. Neural network checkpoints for each iteration/loop step are stored in nn_model_dir
#
#Example call of this script: source train.sh params log.txt
#
#Consumes params file and log file.
#params are defined in pommerman/agents/nn_model/optimize_nn.py
#params should contain:
#n_workers
#start_iteration --note if not blank/0, you should have a checkpoint file (.pt) in your nn_model_dir that is = start_iteration - 1
#max_loop_step
#game_dir
#nn_model_dir
#env_id
#opponent

#Note that 1v1 games are currently not supported by worker.py as the code makes assumptions about having a teammate.
#if a key is missing, default will be attempted (will likely fail if directory paths don't exist)
#if games fail to generate, you will get an assert(len(gameBuffer) == buffer_size) error



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
game_dir="GAMES"
nn_model_dir="NN_MODELS"
env_id="PommeTeamCompetition-v0"
start_iteration=0
opponent="static"

save_param=true

params=''
while IFS=":" read key data
do
    echo "${key} : ${data}"
    if [[ ${key} == 'n_workers' ]]; then
        n_workers=${data}
    fi
    if [[ ${key} == 'start_iteration' ]]; then
        start_iteration=${data}
        save_param=false
    fi
    if [[ ${key} == 'max_loop_step' ]]; then
        max_loop_step=${data}
	max_loop_step=$((max_loop_step + start_iteration))
    fi
    if [[ ${key} == 'game_dir' ]]; then
        game_dir=${data}
    fi
    if [[ ${key} == 'nn_model_dir' ]]; then
        nn_model_dir=${data}
    fi
    if [[ ${key} == 'env_id' ]]; then
        env_id=${data}
    fi
    if [[ ${key} == 'opponent' ]]; then
        opponent=${data}
    fi

    if [ "$save_param" = true ] ; then
        a="--${key}=${data} "
        params=$params$a
    fi
    save_param=true
done < $param_config_file

echo "---all params: $params"
echo "n_workers: $n_workers"
echo "start_iteration: $start_iteration"
echo "max_loop_step: $max_loop_step"
echo "game_dir: $game_dir"
echo "nn_model_dir: $nn_model_dir"
echo "env_id: $env_id"
echo "opponent: $opponent"

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
        python pommerman/agents/worker.py ${params} --device_id="$k" 2>&1 >>$log_file  &
    done
    wait 
}
    

for ((ite=$start_iteration; ite<$max_loop_step; ite++)) do
    echo "iteration $ite"
    play_games $n_workers
    
    wait
    echo "finished working, optimize nn"
    python pommerman/agents/optimize_nn.py ${params} --iteration=$ite 2>&1 >>$log_file
    
    wait
done

echo "Done"
