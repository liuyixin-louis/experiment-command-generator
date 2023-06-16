from config import update_device_command

def parse_base_code(contents, debug = False):
    import re
    indexes = [m.start() for m in re.finditer('#####', contents)]
    
    assert len(indexes) % 2 == 0
    
    # split to span
    spans = []
    # spans.append(contents[:indexes[0]])
    for i in range(len(indexes)):
        if i != len(indexes) - 1:
            spans.append(contents[indexes[i]:indexes[i+1]])
    # spans.append(contents[indexes[-1]:])
        
    spans_with_type = [
        
    ]
    for span in spans:
        if "setup" in span:
            spans_with_type.append((span, "setup"))
        elif "loop" in span:
            spans_with_type.append((span, "loop"))
        elif "main" in span:
            spans_with_type.append((span, "command"))
        else:
            spans_with_type.append((span, "other"))
    
    spans_with_type_added_device_control = []

    for span, type_ in spans_with_type:
        if type_ == "setup":
            spans_with_type_added_device_control.append((
                """cd $(cd "$(dirname "$0")";pwd); source gpu_utility.sh\n\n"""
                , "device_control"))
            spans_with_type_added_device_control.append((span, type_))
            # spans_with_type_added_device_control.append((gpu_env, "device_control"))
            # spans_with_type_added_device_control.append((update_device_func, "device_control"))
        elif type_ == "loop":
            spans_with_type_added_device_control.append((span, type_))
        elif type_ == "command":
            spans_with_type_added_device_control.append((update_device_command, "device_control"))
            span_remove_the_first_part = span[span.index("\n"):]
            if not debug:
                spans_with_type_added_device_control.append((f"\n\ncommand=\"\"\"{span_remove_the_first_part}\"\"\"\n", type_))
                run_command = "eval nohup $command"
                run_command += "  > $log_dir/$RANDOM$RANDOM.log 2>&1 &"
                run_command += "\n\n\n"
                spans_with_type_added_device_control.append((run_command, type_))
            else: 
                spans_with_type_added_device_control.append(
                    (f"{span_remove_the_first_part}\n", type_)
                )
            sleep_command = "sleep $sleeptime\n\n"
            spans_with_type_added_device_control.append((sleep_command, type_))
        else:
            spans_with_type_added_device_control.append((span, type_))
    spans_without_type = [span for span, type_ in spans_with_type_added_device_control]
    spans_without_type_str = "".join(spans_without_type)
    return spans_without_type_str