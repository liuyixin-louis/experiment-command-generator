# import imp
from email.policy import default
import streamlit as st
import pandas as pd
import numpy as np
import time
# import matplotlib.pyplot as plt
# import seaborn as sns
# import plotly.figure_factory as ff
# import altair as alt
# from PIL import Image
# import base64
# import tarfile
# import os
# import requests



# title
st.title("Exp Command Generator")

# experiment mode
exp_mode = st.sidebar.selectbox("Select Experiment Mode", ["OneExpOnecard", "MultipleExpOnecard"],key="MultipleExpOnecard")

## 检查框
debug = st.sidebar.checkbox("Debug:选择则会串行地执行命令", value=True)
# st.sidebar.write(f"checkbox的值是{res}")

setup = st.sidebar.text_area("Some setup of env at beginning.", """cd $(dirname $(dirname $0))
source activate xai
export PYTHONPATH=${PYTHONPATH}:/Users/apple/Desktop/workspace/research_project/attention:/mnt/yixin/:/home/yila22/prj""")

exp_hyper = st.sidebar.text_area("Hyperparameters", """exp_name="debug-adv-training-emotion"
dataset=emotion
n_epoch=3
K=3
encoder=bert
lambda_1=1
lambda_2=1
x_pgd_radius=0.01
pgd_radius=0.001
seed=2
bsize=8
lr=5e-5""")

## gpu 相关参数
gpu_list = st.sidebar.multiselect("multi select", range(10), [5, 6, 7, 8, 9])
# print(gpu_list)
if exp_mode == "OneExpOnecard":
    allow_gpu_memory_threshold_default = 20000
    gpu_threshold_default = 1
elif exp_mode == "MultipleExpOnecard":
    allow_gpu_memory_threshold_default = 3000
    gpu_threshold_default = 70
allow_gpu_memory_threshold = st.sidebar.number_input("最小单卡剩余容量", value=allow_gpu_memory_threshold_default, min_value=0, max_value=30000, step=1000)
gpu_threshold = st.sidebar.number_input("最大单卡利用率", value=gpu_threshold_default, min_value=0, max_value=100, step=10)
sleep_time_after_loading_task= st.sidebar.number_input("加载任务后等待秒数", value=20, min_value=0,step=5)
all_full_sleep_time = st.sidebar.number_input("全满之后等待秒数", value=20, min_value=0,step=5)

gpu_list_str = ' '.join([str(i) for i in gpu_list])
gpu_hyper = f"gpu=({gpu_list_str})\n"
gpu_hyper+=f"allow_gpu_memory_threshold={allow_gpu_memory_threshold}\n"
gpu_hyper+=f"gpu_threshold={gpu_threshold}\n"
gpu_hyper+=f"sleep_time_after_loading_task={sleep_time_after_loading_task}s\n"
gpu_hyper+=f"all_full_sleep_time={all_full_sleep_time}s\n"
gpu_hyper+="gpunum=${#gpu[@]}\n"
gpu_hyper+="i=0\n"

main_loop = st.text_area("Main loop", """for lambda_1 in 1 3;do
  for lambda_2 in 1 10;do
    for n_epoch in 3;do
      for x_pgd_radius in 0.005 0.01;do
        for pgd_radius in 0.0005 0.001 0.002;do
          python train.py --dataset $dataset --data_dir . --output_dir ./outputs/ --attention tanh \
              --encoder $encoder \
                --exp_name $exp_name --lambda_1 $lambda_1 --lambda_2 $lambda_2 --pgd_radius $pgd_radius --x_pgd_radius $x_pgd_radius \
                --K $K  --seed $seed --train_mode adv_train --bsize $bsize --n_epoch $n_epoch --lr $lr \
                --eval_baseline
done;done;done;done;done;""")
if 'python' in main_loop:
    hyper_loop = main_loop.split("python")[0]
    python_cmd = main_loop[main_loop.index('python'):].split('done;')[0]
elif 'bash' in main_loop:
    hyper_loop = main_loop.split("bash")[0]
    python_cmd = main_loop[main_loop.index('bash'):].split('done;')[0]
print(hyper_loop)
print(python_cmd)
end_loop = "done;"*hyper_loop.count("for")
print(end_loop)

g = st.button("Generate")
if g:
    s = ""
    s += setup + "\n\n"
    s += exp_hyper + "\n\n"
    s += gpu_hyper + "\n\n"
    s += hyper_loop + "\n\n"
    s += """
while true; do
    gpu_id=${gpu[$i]}
#    nvidia-smi --query-gpu=utilization.gpu  --format=csv -i 2 | grep -Eo "[0-9]+"
    gpu_u=$(nvidia-smi --query-gpu=utilization.gpu  --format=csv -i $gpu_id | grep -Eo "[0-9]+")
    free_mem=$(nvidia-smi --query-gpu=memory.free --format=csv -i $gpu_id | grep -Eo "[0-9]+")
    if [[ $free_mem -lt $allow_gpu_memory_threshold || $gpu_u -ge ${gpu_threshold} ]]; then
        i=`expr $i + 1`
        i=`expr $i % $gpunum`
        echo "gpu id ${gpu[$i]} is full loaded, skip"
        if [ "$i" == "0" ]; then
            sleep ${all_full_sleep_time}
            echo "all the gpus are full, sleep 1m"
        fi
    else
        break
    fi
done

gpu_id=${gpu[$i]}
# search from the next gpu
i=`expr $i + 1`
i=`expr $i % $gpunum`

free_mem=$(nvidia-smi --query-gpu=memory.free --format=csv -i $gpu_id | grep -Eo "[0-9]+")
gpu_u=$(nvidia-smi --query-gpu=utilization.gpu  --format=csv -i $gpu_id | grep -Eo "[0-9]+")
export CUDA_VISIBLE_DEVICES=$gpu_id
echo "use gpu id is ${gpu[$i]}, free memory is $free_mem, it utilization is ${gpu_u}%"
"""
    s += f"""com="{python_cmd}"\n"""
    s += "echo $com\n"
    s += "echo ==========================================================================================\n"
    if debug:
        s += "$com\n"
        s += "# mkdir -p ./logs/\n"
        s += "# nohup $com > ./logs/$exp_name-$RANDOM.log 2>&1 &\n"
    else:
        s += "# $com\n"
        s += "mkdir -p ./logs/\n"
        s += "nohup $com > ./logs/$exp_name-$RANDOM.log 2>&1 &\n"
    s += """echo "sleep for $sleep_time_after_loading_task to wait the task loaded"
    sleep  $sleep_time_after_loading_task\n"""
    s += end_loop
    st.success("Finished")
    st.code(s, language="shell")
  

  


