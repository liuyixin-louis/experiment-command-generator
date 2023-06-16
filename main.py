# import imp
from email.policy import default
import streamlit as st
import pandas as pd
import numpy as np
import time
from config import  update_device_func
from parse_code import parse_base_code


# title
st.title("Exp Command Generator")

# experiment mode
# exp_mode = st.sidebar.selectbox("Select Experiment Mode", ["OneExpOnecard", "MultipleExpOnecard"],key="MultipleExpOnecard")

## 检查框
debug = st.sidebar.checkbox("Debug: 选择则会串行地执行命令", value=True)
# st.sidebar.write(f"checkbox的值是{res}")

# setup = st.sidebar.text_area("Some setup of env at beginning.", """cd $(dirname $(dirname $0))
# source activate xai
# export PYTHONPATH=${PYTHONPATH}:/Users/apple/Desktop/workspace/research_project/attention:/mnt/yixin/:/home/yila22/prj""")

# exp_hyper = st.sidebar.text_area("Hyperparameters", """exp_name="debug-adv-training-emotion"
# dataset=emotion
# n_epoch=3
# K=3
# encoder=bert
# lambda_1=1
# lambda_2=1
# x_pgd_radius=0.01
# pgd_radius=0.001
# seed=2
# bsize=8
# lr=5e-5""")

## gpu 相关参数
gpu_list = st.sidebar.multiselect("multi select", range(10), [0,1,2,3,4,])
# print(gpu_list)
allow_gpu_memory_threshold_default=5000
gpu_threshold_default=90
total_gpu_memory = st.sidebar.number_input("单卡总容量", value=24564, min_value=0, max_value=30000, step=1000)
max_gpu_memory_gap = st.sidebar.number_input("最小单卡剩余容量", value=allow_gpu_memory_threshold_default, min_value=0, max_value=total_gpu_memory, step=500)
max_gpu_utilization = st.sidebar.number_input("最大单卡利用率", value=gpu_threshold_default, min_value=0, max_value=100, step=10)
sleep_time_after_loading_task= st.sidebar.number_input("加载任务后等待秒数", value=10, min_value=0,step=5)
# all_full_sleep_time = st.sidebar.number_input("全满之后等待秒数", value=20, min_value=0,step=5)
username = st.sidebar.text_input("用户名", value="yila22")
cpu_max_utility = st.sidebar.number_input("cpu最大利用率", value=77, min_value=0, max_value=100, step=1)
memory_max_utility = st.sidebar.number_input("内存最大利用率", value=80, min_value=0, max_value=100, step=1)
constrain_total = st.sidebar.checkbox("限制总资源", value=True)
constrain_mine = st.sidebar.checkbox("限制我的资源", value=False)
constrain_rate = st.sidebar.number_input("限制率", value=2, min_value=1, max_value=10, step=1)

# username_mine=root
# max_gpu_utilization=90
# total_gpu_memory=24564
# max_gpu_memory_gap=5000
# available_devices=( 0 1 2 3 4 5 6 7 8 9 )
# current_device_idx=-1
# sleeptime=30
# cpu_mean_max=77
# memory_rate_max=80
# constrain_total=true
# constrain_mine=false
# constrain_rate=2
gpu_list = " ".join([str(i) for i in gpu_list])
setup_for_gpu_utility = f"""
username={username}
# available_devices=( 0 1 2 3 4 )
# available_devices=( 5 6 7 8 9 )
# available_devices=( 0 1 2 3 4 5 6 7 8 9 )
available_devices=( {gpu_list} )
max_gpu_utilization={max_gpu_utilization}
total_gpu_memory={total_gpu_memory}
max_gpu_memory_gap={max_gpu_memory_gap}
current_device_idx=-1
sleeptime={sleep_time_after_loading_task}
cpu_mean_max={cpu_max_utility}
memory_rate_max={memory_max_utility}
constrain_total={"true" if constrain_total else "false"}
constrain_mine={"true" if constrain_mine else "false"}
constrain_rate={"true" if constrain_rate else "false"}
"""


base_code = st.text_area("Base Code", """##### setup
export CUDA_VISIBLE_DEVICES=2
source activate /data/yixin/anaconda/mib
exp_name="single_user"
#####

##### loop
for poison_method in char_basic word_basic sent_basic; do
for dataset_idx in 0 1 2; do
#####

##### main
  python single_user.py --dataset_idx $dataset_idx --trigger_size 1 --target 0 \
   --loc 0 --batch_size 16 --num_epochs 2 --poison_method $poison_method --lr 5e-5 --pattern 0 --exp_name $exp_name \
    --log_wb
#####

#####
done;done;
#####""", height=400)



g = st.button("Generate")
if g:
    st.success("Finished")
    contents = base_code
    gpu_utility = ""
    gpu_utility = setup_for_gpu_utility + "\n\n" + update_device_func 
    
    
    new_code = parse_base_code(contents, debug=debug)
    
    # create file for download 
    timestr = time.strftime("%Y%m%d-%Hh%Mm%Ss")
    import os 
    os.makedirs(f"./res/{timestr}", exist_ok=True)
    filename_script = f"./res/{timestr}/script.sh"
    with open(filename_script, "w") as f:
        f.write(new_code)
    filename_config = f"./res/{timestr}/gpu_utility.sh"
    with open(filename_config, "w") as f:
        f.write(gpu_utility)
    
    # zip them into one file
    # import shutil
    # shutil.make_archive(f"./res/{timestr}", 'zip', f"./res/{timestr}")
    # st.download_button(
    #     label="Download zip",
    #     data=f"./res/{timestr}.zip",
    #     file_name=f"{timestr}.zip",
    #     mime="application/zip",
    # )
    
    
    st.download_button(
        label="Download script",
        data=new_code,
        file_name=filename_script,
        mime="text/plain",
    )
    # after clicking i don't want the website to refresh
    st.download_button(
        label="Download gpu_utility.sh",
        data=gpu_utility,
        file_name=filename_config,
        mime="text/plain",
    )
    
    # st.markdown(f"### [Download script](./{filename_script})")
    # st.markdown(f"### [Download gpu_utility.sh](P{filename_config})")
    st.markdown("## script.sh")
    st.code(new_code, language="shell")
    
    
    st.markdown("## gpu_utility.sh")
    st.code(gpu_utility, language="shell")
    
    


