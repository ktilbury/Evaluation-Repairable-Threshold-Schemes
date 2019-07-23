#!/usr/bin/python3

from repair import *

import random as r
import pandas as pd
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


def evaluate_design(blocks, availability_probs, fault_models, num_iterations, repair_algorithms):
    # Instantiate participants and add to dict
    participants = {}
    for i, block in enumerate(blocks):
        p = Participant(i, block)
        participants.update({i: p})
    # Initialize extra participant attributes
    init_intersecting_participants(participants)
    init_grouped_participants(participants)

    # Initialize dataframe to save results to
    df = pd.DataFrame(columns=['Algorithm', 'Fault model', 'Availability probability',
                               'Successful repairs', 'Success total contacted', 'Success average contacted',
                               'Total success wall clock time', 'Average success wall clock time',
                               'Total success process time', 'Average success process time',
                               'Failed repairs', 'Fail total contacted', 'Fail average contacted',
                               'Total fail wall clock time', 'Average fail wall clock time',
                               'Total fail process time', 'Average fail process time'])

    # Loop through so many things
    for repair_algo in repair_algorithms:
        for fault_model in fault_models:
            for prob in availability_probs:
                repair_wall_time = 0.0
                repair_process_time = 0.0
                total_success_contacted = 0

                failed_repairs = 0
                fail_wall_time = 0.0
                fail_process_time = 0.0
                total_failed_contacted = 0

                for i in range(num_iterations):

                    participant_to_repair = participants.get((r.sample(participants.keys(), 1)[0]))
                    participants_copy = participants.copy()  # send copy of dict to algo 1 so can pop from dict for
                    # permanent fault
                    participants_copy.pop(
                        participant_to_repair.id_num)  # remove ptcpnt to repair from dict so don't contact self

                    start_wall_time = time.clock()
                    start_process_time = time.process_time()
                    success, participants_contacted = repair_algo(participants_copy, participant_to_repair,
                                                                  prob, fault_model)
                    end_wall_time = (time.clock() - start_wall_time)
                    end_process_time = (time.process_time() - start_process_time)

                    if success:
                        repair_wall_time += end_wall_time
                        repair_process_time += end_process_time
                        total_success_contacted += participants_contacted
                    elif not success:
                        failed_repairs += 1
                        fail_wall_time += end_wall_time
                        fail_process_time += end_process_time
                        total_failed_contacted += participants_contacted

                success_repairs = num_iterations - failed_repairs

                results = {}
                results.update({'Algorithm': str(repair_algo.__name__)})
                results.update({'Fault model': fault_model})
                results.update({'Availability probability': prob})
                results.update({'Fault model': fault_model})
                if success_repairs > 0:
                    results.update({'Successful repairs': success_repairs})
                    results.update({'Success total contacted': total_success_contacted})
                    results.update({'Success average contacted': (total_success_contacted / success_repairs)})
                    results.update({'Total success wall clock time': repair_wall_time})
                    results.update({'Average success wall clock time': (repair_wall_time / success_repairs)})
                    results.update({'Total success process time': repair_process_time})
                    results.update({'Average success process time': (repair_process_time / success_repairs)})
                else:
                    results.update({'Successful repairs': 0})
                    results.update({'Success total contacted': None})
                    results.update({'Success average contacted': None})
                    results.update({'Total success wall clock time': None})
                    results.update({'Average success wall clock time': None})
                    results.update({'Total success process time': None})
                    results.update({'Average success process time': None})

                if failed_repairs > 0:
                    results.update({'Failed repairs': failed_repairs})
                    results.update({'Fail total contacted': total_failed_contacted})
                    results.update({'Fail average contacted': (total_failed_contacted / failed_repairs)})
                    results.update({'Total fail wall clock time': fail_wall_time})
                    results.update({'Average fail wall clock time': (fail_wall_time / failed_repairs)})
                    results.update({'Total fail process time': fail_process_time})
                    results.update({'Average fail process time': (fail_process_time / failed_repairs)})
                else:
                    results.update({'Failed repairs': 0})
                    results.update({'Fail total contacted': None})
                    results.update({'Fail average contacted': None})
                    results.update({'Total fail wall clock time': None})
                    results.update({'Average fail wall clock time': None})
                    results.update({'Total fail process time': None})
                    results.update({'Average fail process time': None})

                df = df.append(results, ignore_index=True)
    return df


"""
Test algorithm
"""
design_blocks = [[0, 1, 3], [0, 2, 6], [0, 4, 5], [1, 2, 4], [1, 5, 6], [2, 3, 5], [3, 4, 6]]
avail_probs = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
fault_models_list = ["Permanent", "Transient"]
num_repair_iterations = 1
repair_algos_list = [random_participants, stored_intersecting_participants, stored_grouped_participants]

data = evaluate_design(design_blocks, avail_probs, fault_models_list, num_repair_iterations, repair_algos_list)

print(data)


