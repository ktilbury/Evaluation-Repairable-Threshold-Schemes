#!/usr/bin/python3

from participant import Participant

import random as r
import time
import numpy as np


def get_shares(missing_shares, available_shares):
    return list(set(missing_shares).intersection(available_shares))


def random_participants(participant_dic, failed_participant, p_available, fault="Transient"):
    faults = ["Permanent", "Transient"]
    assert fault in faults

    failed_participant.missing_shares = failed_participant.shares

    steps = 0
    repaired = False
    while not repaired:
        P_id = np.random.choice(list(participant_dic))
        if P_id == failed_participant.id_num:  # don't contact self
            continue

        P = participant_dic[P_id]
        steps += 1

        if fault == "Transient":
            if np.random.random_sample() > p_available:
                continue
        if fault == "Permanent":
            if not P.is_available():
                participant_dic.pop(P_id)  # remove from the dict and don't consider contacting again
                continue
            else:
                if np.random.random_sample() > p_available:
                    P.available = False
                    participant_dic.pop(P_id)  # remove from the dict and don't consider contacting again
                    continue

        shares = get_shares(failed_participant.missing_shares, P.shares)
        if shares:
            failed_participant.missing_shares.remove(shares[0])
            if not failed_participant.missing_shares:
                repaired = True
    return True  # return True that repair was successful, will need a fail condition when using permanant fault

"""
Test algorithm
"""
blocks = [[0, 1, 3], [0, 2, 6], [0, 4, 5], [1, 2, 4], [1, 5, 6], [2, 3, 5], [3, 4, 6]]
availability_probabilities = [1] #, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
fault_model = "Transient"
participants = {}
num_iterations = 1

# Instantiate participants and add to dict
for i, block in enumerate(blocks):
    p = Participant(i, block)
    participants.update({i: p})

# Iterate through availability probabilities: time repairs and count failed repairs at each probability
for prob in availability_probabilities:
    repair_wall_time = 0.0
    repair_process_time = 0.0
    failed_repairs = 0

    for i in range(num_iterations):

        participant_to_repair = participants.get((r.sample(participants.keys(), 1)[0]))

        start_wall_time = time.clock()
        start_process_time = time.process_time()

        if random_participants(participants, participant_to_repair, prob, fault_model):
            repair_wall_time += (time.clock() - start_wall_time)
            repair_process_time += (time.process_time() - start_process_time)
        else:
            failed_repairs += 1

    success_repairs = num_iterations - failed_repairs
    avg_wall_time = repair_wall_time/success_repairs
    avg_process_time = repair_process_time/success_repairs

    print("Availability probabilty: " + str(prob) + "\n" +
          "Failed repairs: " + str(failed_repairs) + "\n" +
          "Total wall clock time of " + str(repair_wall_time) + " with average of " + str(avg_wall_time) + " per repair" + "\n" +
          "Total process time of " + str(repair_process_time) + " with average of " + str(avg_process_time) + " per repair")