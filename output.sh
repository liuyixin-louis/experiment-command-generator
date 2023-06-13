cd $(cd "$(dirname "$0")";pwd); source gpu_utility.sh

##### setup
#!/bin/bash
file_name=$(basename $0)
current_path=$(pwd)
cd /data/yixin/workspace/unl-graph-usenix
source activate /data/yixin/anaconda/unlg
datasets=("IMDB-BINARY"  "MUTAG" "ENZYMES" "IMDB-MULTI"  )
models=( "gcn" "gin"  "sage" )
entity="mib-nlp"
exp_name="adv-run-v3"
batch_size=8
methods=( "clean" "rand"  "feat" "grad" "inject"  "adv")
wd=1e-5
adv_train_budgets=( 0.07 0.09 0.11 )
gen_exp_name="main-results-v2"
lr=0.01
es_patience=40
seed_default=0
optimizer="adam"
budget=0.05
total_epoch=300
max_steps=5000
seeds=("402")
# mkdir $current_path/logs/ if not exist
mkdir -p $current_path/logs/
mkdir -p $current_path/logs/$exp_name
#####



##### loop
for adv_train_budget in "${adv_train_budgets[@]}"; do
for dataset in "${datasets[@]}"; do
for model in "${models[@]}"; do
for method in "${methods[@]}"; do
##### 

    
update_device_idx;


command="""
    comb_command="for seed in ${seeds[@]} ; do nohup python eval.py --dataset $dataset --model ${model} --method ${method} --lr $lr --exp_name $exp_name --entity $entity  --batch_size $batch_size --seed \$seed --early_stop --num_epochs $total_epoch --wd $wd --device $device --es_patience $es_patience --optimizer $optimizer --max_steps $max_steps --adv_train --adv_train_budget $adv_train_budget --gen_exp_name $gen_exp_name > $current_path/logs/$exp_name/$dataset.$model.$method-\$seed-$RANDOM$RANDOM.log 2>&1 ; done; "
    eval $comb_command & 
    
    """
eval $command


##### 

##### 
done;
done;
done;
done;
