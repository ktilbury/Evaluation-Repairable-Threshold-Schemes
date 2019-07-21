#!/usr/bin/python3

from repair import *

import random as r
import time


def init_intersecting_participants(participants_dic):
    """
    Initialization function to set up the intersecting participants list for each of the participant objects
    :param participants_dic: the full set of participants
    """
    for id_num, participant in participants_dic.items():
        for other_participant in participants_dic.values():
            if id_num == other_participant.id_num:  # skip self
                continue
            if not set(participant.shares).isdisjoint(other_participant.shares):
                participant.intersecting_participants.append(other_participant.id_num)


def init_grouped_participants(participants_dic):
    """
    Initialization function to set up the grouped participants dictionary for each of the participant objects
    :param participants_dic:
    """
    for id_num, participant in participants_dic.items():
        for s in participant.shares:
            participant.grouped_participants.update({s: []})
        for other_participant in participants_dic.values():
            if id_num == other_participant.id_num:  # skip self
                continue
            for s in participant.shares:
                if s in other_participant.shares:
                    l = participant.grouped_participants.get(s)
                    l.append(other_participant.id_num)
                    participant.grouped_participants[s] = l.copy()

"""
Test algorithm
"""
blocks = [[0, 1, 3], [0, 2, 6], [0, 4, 5], [1, 2, 4], [1, 5, 6], [2, 3, 5], [3, 4, 6]]
availability_probabilities = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
fault_model = "Permanent"
# fault_model = "Transient"
num_iterations = 10000

# Instantiate participants and add to dict
participants = {}
for i, block in enumerate(blocks):
    p = Participant(i, block)
    participants.update({i: p})
# Initialize extra participant attributes
init_intersecting_participants(participants)
init_grouped_participants(participants)

# Iterate through availability probabilities: time repairs and count failed repairs at each probability
for prob in availability_probabilities:
    repair_wall_time = 0.0
    repair_process_time = 0.0
    total_success_contacted = 0

    failed_repairs = 0
    fail_wall_time = 0.0
    fail_process_time = 0.0
    total_failed_contacted = 0

    for i in range(num_iterations):

        participant_to_repair = participants.get((r.sample(participants.keys(), 1)[0]))
        participants_copy = participants.copy()  # send copy of dict to algo 1 so can pop from dict for permanent fault
        participants_copy.pop(participant_to_repair.id_num)  # remove ptcpnt to repair from dict so don't contact self

        start_wall_time = time.clock()
        start_process_time = time.process_time()
        success, participants_contacted = random_participants(participants_copy, participant_to_repair, prob, fault_model)
        end_wall_time = (time.clock() - start_wall_time)
        end_process_time = (time.process_time() - start_process_time)

        if success:
            repair_wall_time += end_wall_time
            repair_process_time += end_process_time
            total_success_contacted += participants_contacted
        elif not success:
            failed_repairs += 1
            total_failed_contacted += participants_contacted

    success_repairs = num_iterations - failed_repairs
    print("___________________________________________________________________________________________________________")
    print("Fault model: " + fault_model)
    print("Availability probabilty: " + str(prob))

    if success_repairs > 0:
        print("Successful repairs: " + str(success_repairs))
        print("Total participants contacted: " + str(total_success_contacted))
        print("Average participants contacted: " + str(total_success_contacted/success_repairs))
        print("Total repair wall clock time: " + str(repair_wall_time))
        print("Average repair wall clock time: " + str(repair_wall_time/success_repairs))
        print("Total repair process time: " + str(repair_process_time))
        print("Average repair process time: " + str(repair_process_time/success_repairs))
    else:
        print("Successful repairs: 0")
    if failed_repairs > 0:
        print("Failed repairs: " + str(failed_repairs))
        print("Total participants contacted: " + str(total_failed_contacted))
        print("Average participants contacted: " + str(total_failed_contacted/failed_repairs))
        print("Total fail wall clock time: " + str(fail_wall_time))
        print("Average fail wall clock time: " + str(fail_wall_time / failed_repairs))
        print("Total fail process time: " + str(fail_process_time))
        print("Average fail process time: " + str(fail_process_time / failed_repairs))
    else:
        print("Failed repairs: 0")