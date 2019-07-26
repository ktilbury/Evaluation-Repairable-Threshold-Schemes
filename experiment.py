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
avail_probs = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
fault_models_list = ["Permanent", "Transient"]
num_repair_iterations = 1000
repair_algos_list = [random_participants, stored_intersecting_participants, stored_grouped_participants]

print("Evaluating...")
# design (7, 7, 3, 3, 1)-BIBD, gives threshold of 2
d_blocks = [[0, 1, 3], [0, 2, 6], [0, 4, 5], [1, 2, 4], [1, 5, 6], [2, 3, 5], [3, 4, 6]]
data = evaluate_design(d_blocks, avail_probs, fault_models_list, num_repair_iterations, repair_algos_list)
data.to_csv("7,7,3,3,1-BIBD_results.csv", encoding='utf-8', index=False)
print("Done.")

print("Evaluating...")
# design (9, 12, 4, 3, 1)-BIBD
d_blocks = [[0, 3, 6], [0, 4, 7], [2, 4, 6], [6, 7, 8], [0, 5, 8], [3, 4, 5], [2, 3, 8], [2, 5, 7], [1, 4, 8],
            [1, 3, 7], [0, 1, 2], [1, 5, 6]]
data = evaluate_design(d_blocks, avail_probs, fault_models_list, num_repair_iterations, repair_algos_list)
data.to_csv("9,12,4,3,1-BIBD_results.csv", encoding='utf-8', index=False)
print("Done.")

print("Evaluating...")
# design (13, 13, 4, 4, 1)-BIBD
d_blocks = [[0, 2, 4, 6], [6, 8, 10, 12], [6, 7, 9, 11], [0, 5, 8, 9], [4, 5, 10, 11], [0, 3, 11, 12], [3, 4, 7, 8],
            [2, 3, 9, 10], [1, 4, 9, 12], [2, 5, 7, 12], [1, 3, 5, 6], [1, 2, 8, 11], [0, 1, 7, 10]]
data = evaluate_design(d_blocks, avail_probs, fault_models_list, num_repair_iterations, repair_algos_list)
data.to_csv("13,13,4,4,1-BIBD_results.csv", encoding='utf-8', index=False)
print("Done.")

print("Evaluating...")
# design (16, 20, 5, 4, 1)-BIBD
d_blocks = [[0, 1, 13, 15], [2, 5, 11, 12], [3, 5, 10, 15], [9, 11, 14, 15], [9, 10, 12, 13], [0, 2, 6, 10],
            [0, 3, 8, 11], [7, 8, 10, 14], [6, 8, 12, 15], [0, 4, 12, 14], [0, 5, 7, 9], [6, 7, 11, 13], [4, 5, 8, 13],
            [3, 4, 6, 9], [2, 4, 7, 15], [2, 3, 13, 14], [1, 5, 6, 14], [1, 4, 10, 11], [1, 3, 7, 12], [1, 2, 8, 9]]
data = evaluate_design(d_blocks, avail_probs, fault_models_list, num_repair_iterations, repair_algos_list)
data.to_csv("16,20,5,4,1-BIBD_results.csv", encoding='utf-8', index=False)
print("Done.")

print("Evaluating...")
# design (21, 21, 5, 5, 1)-BIBD
d_blocks = [[2, 4, 7, 9, 10], [2, 5, 11, 16, 20], [0, 1, 10, 11, 12], [1, 9, 13, 16, 17], [3, 10, 13, 15, 20],
            [0, 9, 14, 19, 20], [1, 4, 8, 18, 20], [7, 8, 11, 13, 14], [1, 5, 7, 15, 19], [6, 8, 10, 16, 19],
            [6, 7, 12, 17, 20], [0, 4, 5, 6, 13], [3, 5, 8, 9, 12], [3, 4, 11, 17, 19], [1, 2, 3, 6, 14],
            [5, 10, 14, 17, 18], [2, 12, 13, 18, 19], [4, 12, 14, 15, 16], [6, 9, 11, 15, 18], [0, 3, 7, 16, 18],
            [0, 2, 8, 15, 17]]
data = evaluate_design(d_blocks, avail_probs, fault_models_list, num_repair_iterations, repair_algos_list)
data.to_csv("21,21,5,5,1-BIBD_results.csv", encoding='utf-8', index=False)
print("Done.")

print("Evaluating...")
# design (25, 30, 6, 5, 1)-BIBD, gives threshold of 2 or 3 depending on base scheme and repairing degree d of 5
d_blocks = [[9, 11, 16, 18, 21], [3, 10, 16, 19, 23], [5, 8, 10, 20, 22], [6, 15, 17, 18, 22], [3, 5, 7, 14, 18],
            [3, 6, 9, 20, 24], [0, 9, 10, 13, 17], [0, 11, 14, 19, 22], [2, 13, 18, 19, 20], [2, 4, 16, 22, 24],
            [11, 12, 15, 20, 23], [2, 5, 17, 21, 23], [10, 14, 15, 21, 24], [0, 8, 18, 23, 24], [2, 8, 9, 12, 14],
            [2, 6, 7, 10, 11], [7, 8, 13, 15, 16], [7, 12, 17, 19, 24], [0, 5, 6, 12, 16], [4, 6, 13, 14, 23],
            [4, 5, 9, 15, 19], [3, 4, 8, 11, 17], [0, 4, 7, 20, 21], [3, 12, 13, 21, 22], [1, 6, 8, 19, 21],
            [1, 5, 11, 13, 24], [1, 4, 10, 12, 18], [0, 1, 2, 3, 15], [1, 7, 9, 22, 23], [1, 14, 16, 17, 20]]
data = evaluate_design(d_blocks, avail_probs, fault_models_list, num_repair_iterations, repair_algos_list)
data.to_csv("25,30,6,5,1-BIBD_results.csv", encoding='utf-8', index=False)
print("Done.")

print("Evaluating...")
# design (31, 31, 6, 6, 1)-BIBD
d_blocks = [[0, 5, 8, 24, 27, 28], [2, 6, 10, 15, 28, 29], [2, 3, 5, 9, 11, 20], [3, 6, 7, 19, 23, 27],
            [4, 6, 11, 17, 24, 25], [9, 12, 16, 19, 25, 28], [7, 9, 18, 24, 29, 30], [10, 13, 19, 20, 21, 24],
            [11, 13, 18, 23, 26, 28], [2, 14, 16, 22, 23, 24], [14, 15, 18, 20, 25, 27], [9, 10, 17, 22, 26, 27],
            [0, 3, 13, 22, 25, 29], [8, 12, 17, 20, 23, 29], [8, 11, 15, 19, 22, 30], [0, 6, 16, 20, 26, 30],
            [2, 7, 8, 21, 25, 26], [5, 7, 13, 15, 16, 17], [0, 7, 10, 11, 12, 14], [5, 6, 12, 18, 21, 22],
            [4, 5, 14, 19, 26, 29], [0, 4, 9, 15, 21, 23], [3, 4, 8, 10, 16, 18], [2, 4, 12, 13, 27, 30],
            [3, 14, 17, 21, 28, 30], [1, 6, 8, 9, 13, 14], [1, 5, 10, 23, 25, 30], [0, 1, 2, 17, 18, 19],
            [1, 4, 7, 20, 22, 28], [1, 3, 12, 15, 24, 26], [1, 11, 16, 21, 27, 29]]
data = evaluate_design(d_blocks, avail_probs, fault_models_list, num_repair_iterations, repair_algos_list)
data.to_csv("31,31,6,6,1-BIBD_results.csv", encoding='utf-8', index=False)
print("Done.")

print("Evaluating...")
# design (36, 42, 7, 6, 1)-BIBD
d_blocks = [[2, 4, 10, 12, 29, 35], [2, 5, 8, 24, 29, 35], [0, 3, 10, 13, 29, 35], [2, 6, 9, 13, 29, 35],
            [4, 17, 20, 24, 29, 35], [2, 7, 14, 17, 29, 35], [3, 6, 8, 14, 29, 35], [3, 7, 12, 16, 28, 34],
            [4, 7, 8, 15, 28, 34], [5, 11, 12, 14, 24, 34], [9, 11, 20, 23, 28, 34], [10, 11, 19, 23, 28, 34],
            [13, 15, 19, 23, 28, 34], [14, 18, 19, 23, 28, 34], [0, 14, 19, 23, 28, 33], [17, 18, 19, 23, 27, 33],
            [6, 15, 20, 23, 24, 33], [18, 19, 20, 22, 27, 33], [16, 18, 19, 22, 27, 33], [0, 12, 15, 17, 27, 33],
            [7, 9, 20, 22, 24, 33], [12, 13, 18, 22, 27, 32], [9, 10, 14, 15, 16, 32], [8, 11, 13, 16, 17, 32],
            [8, 10, 18, 22, 27, 32], [8, 9, 12, 22, 27, 32], [0, 6, 7, 11, 26, 32], [5, 7, 13, 22, 26, 32],
            [5, 6, 10, 17, 26, 31], [4, 6, 16, 21, 26, 31], [0, 4, 5, 9, 26, 31], [3, 5, 15, 21, 26, 31],
            [3, 4, 11, 21, 26, 31], [2, 3, 18, 21, 25, 31], [1, 7, 10, 21, 25, 31], [1, 6, 12, 21, 25, 30],
            [1, 5, 16, 21, 25, 30], [0, 2, 16, 20, 24, 30], [1, 4, 13, 14, 25, 30], [1, 3, 9, 17, 25, 30],
            [0, 1, 8, 20, 24, 30], [1, 2, 11, 15, 25, 30]]
data = evaluate_design(d_blocks, avail_probs, fault_models_list, num_repair_iterations, repair_algos_list)
data.to_csv("36,42,7,6,1-BIBD_results.csv", encoding='utf-8', index=False)
print("Done.")
