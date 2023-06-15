cd $(cd "$(dirname "$0")";pwd); source gpu_utility.sh

##### setup
export CUDA_VISIBLE_DEVICES=2
source activate /data/yixin/anaconda/mib
exp_name="single_user"
#####

##### loop
for poison_method in char_basic word_basic sent_basic; do
for dataset_idx in 0 1 2; do
#####


update_device_idx;


command="""
  python single_user.py --dataset_idx $dataset_idx --trigger_size 1 --target 0    --loc 0 --batch_size 16 --num_epochs 2 --poison_method $poison_method --lr 5e-5 --pattern 0 --exp_name $exp_name     --log_wb
"""
eval $command &


sleep $sleeptime

#####

#####
done;
