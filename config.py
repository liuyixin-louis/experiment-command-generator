
update_device_command = "update_device_idx;\n"

update_device_func = """
function update_device_idx {
    if [ $constrain_total = true ]; then
    # check total cpu usage
    while true; do
        cpu_mean_1=$(mpstat -P ALL 1 1 | awk '/Average:/ && $2 ~ /[0-9]/ { cpu_usage=100-$NF; total+=cpu_usage; count++ } END { print total/count }')
        sleep 1
        cpu_mean_2=$(mpstat -P ALL 1 1 | awk '/Average:/ && $2 ~ /[0-9]/ { cpu_usage=100-$NF; total+=cpu_usage; count++ } END { print total/count }')
        sleep 1
        cpu_mean_3=$(mpstat -P ALL 1 1 | awk '/Average:/ && $2 ~ /[0-9]/ { cpu_usage=100-$NF; total+=cpu_usage; count++ } END { print total/count }')
        cpu_mean=$(echo "scale=2; ($cpu_mean_1+$cpu_mean_2+$cpu_mean_3)/3" | bc)

        # if currently cpu usage is less than the threshold, then break
        if [ $(echo "$cpu_mean < $cpu_mean_max" | bc) -eq 1 ]; then
            echo "total cpu mean: $cpu_mean is less than $cpu_mean_max, continue to check total memory usage"
            break
        else
            echo "total cpu mean: $cpu_mean is greater than $cpu_mean_max, sleep 10 seconds"
            sleep 10
        fi
    done;

    # check total memory usage
    while true; do
        # get memory usage of whole system
        mem_used_1=$(free -m | awk '/Mem:/ {print $3}')
        sleep 1
        mem_used_2=$(free -m | awk '/Mem:/ {print $3}')
        sleep 1
        mem_used_3=$(free -m | awk '/Mem:/ {print $3}')
        mem_used=$(echo "scale=2; ($mem_used_1+$mem_used_2+$mem_used_3)/3" | bc)
        
        # echo $mem_used
        # get rate of memory usage
        mem_rate=$(echo "scale=2; $mem_used/$(free -m | awk '/Mem:/ {print $2}')*100" | bc)
        # echo $mem_rate
        if [ $(echo "$mem_rate < $memory_rate_max" | bc) -eq 1 ]; then
            echo "total memory rate: $mem_rate is less than $memory_rate_max, continue to check my own cpu and memory usage"
            break
        else
            echo "total memory rate: $mem_rate is greater than $memory_rate_max, sleep 10 seconds"
            sleep 10
        fi
    done;
    fi;

    # if constrain_mine
    if [ $constrain_mine = true ]; then

        # check my own cpu and memory usage, it should be less than 1/$constrain_rate of the given cpu_mean_max / memory_rate_max
        while true; do
            username=$username_mine
            cpu_usage_user_sum=$(ps -u $username -o %cpu | awk '{sum+=$1} END {print sum}')
            # echo $cpu_usage_user_sum
            total_aviable_cpu=$(nproc)
            total_aviable_cpu=$(echo "$total_aviable_cpu*100" | bc)
            # echo $total_aviable_cpu
            cpu_usage_user_ratio=$(echo "scale=2; $cpu_usage_user_sum/$total_aviable_cpu*100" | bc)
            # echo $cpu_usage_user_ratio

            memory_usage_user_sum=$(ps -u $username -o rss | awk '{sum+=$1} END {print sum/1024}')
            # echo $memory_usage_user_sum
            memory_usage_total=$(free -m | awk '/Mem:/ {print $2}')
            # echo $memory_usage_total
            memory_usage_user_ratio=$(echo "scale=2; $memory_usage_user_sum/$memory_usage_total*100" | bc)
            # echo $memory_usage_user_ratio

            # so my ratio should be less than 1/$constrain_rate of the given threshold
            cpu_mean_max_mine=$(echo "$cpu_mean_max/$constrain_rate" | bc)
            memory_rate_max_mine=$(echo "$memory_rate_max/$constrain_rate" | bc)
            if [ $(echo "$cpu_usage_user_ratio < $cpu_mean_max_mine" | bc) -eq 1 ] && [ $(echo "$memory_usage_user_ratio < $memory_rate_max_mine" | bc) -eq 1 ]; then
                echo "my cpu usage: $cpu_usage_user_ratio, memory usage: $memory_usage_user_ratio is less than half of the given threshold for cpu: $cpu_mean_max_mine and memory: $memory_rate_max_mine, ready to take off"
                break
            else
                echo "my cpu usage: $cpu_usage_user_ratio, memory usage: $memory_usage_user_ratio is greater than half of the given threshold, sleep 10 seconds"
                sleep 10
            fi
        done;
    fi;

    # so all the conditions are satisfied, we can update the device idx and run the next experiment
    while true; do
        current_device_idx=$((current_device_idx+1))
        if [ $current_device_idx -ge ${#available_devices[@]} ]; then
            # reset 
            current_device_idx=0
        fi
        # check whether this device is fully booked using nvidia-smi
        # get the gpu current memory usage 
        useage=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i ${available_devices[$current_device_idx]})
        utilization=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits -i ${available_devices[$current_device_idx]})
        
        if [ $useage -ge $((total_gpu_memory-max_gpu_memory_gap)) ] || [ $utilization -ge $max_gpu_utilization ]; then
            echo "device ${available_devices[$current_device_idx]} is fully booked, try next one"
            sleep 3
            continue
        else
            break
        fi
    done
    echo "current device: ${available_devices[$current_device_idx]}"
    device=${available_devices[$current_device_idx]}
}
"""