def cost_func(graph, array, max_duration):
    total_cost = 0

    # Params
    COST = 0.1/60  # Cost per second
    BOOTING_TIME = 5*60
    PENALTY_MULTIPLIER = 2
    
    # Number of machines used by the individual
    machines_number = max(map(lambda x: x[1], array))

    # Array of finishing times of the last task of a given machine
    time_machine = [0] * (machines_number + 1)

    # Array of finishing time of a given task
    time_task = [0] * len(array)

    for task, machine in array:
        last_task_ending_time = time_machine[machine]
        starting_time = last_task_ending_time
        duration = graph.nodes[task]['data']
        for key in graph.predecessors(task):
            starting_time = max(starting_time,
                                time_task[int(key)])  # task cannot start while its dependencies are not finished
        finishing_time = starting_time + duration
        time_machine[machine] = finishing_time
        time_task[int(task)] = finishing_time
        if last_task_ending_time == 0:  # If it is the first task of the machine
            total_cost += COST * (BOOTING_TIME + duration)
            if starting_time < BOOTING_TIME:  # We have to boot the machine before executing the task
                time_machine[machine] += BOOTING_TIME
                time_task[int(task)] += BOOTING_TIME
        elif starting_time - last_task_ending_time > BOOTING_TIME:  # We have to reboot the machine before executing the task
            total_cost += COST * (BOOTING_TIME + duration)
        else:  # The machine stays on between the last task and this task
            total_cost += COST * (finishing_time - last_task_ending_time)

    total_duration = max(time_machine)

    # Penalty when the individual does not respect the constraint
    if total_duration > max_duration:
        total_cost *= PENALTY_MULTIPLIER
    return (total_cost, total_duration)
