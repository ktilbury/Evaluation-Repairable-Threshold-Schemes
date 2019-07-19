#!/usr/bin/python3

from participant import Participant

import random as r
import time
import numpy as np


def init_intersecting_participants(participants_dic):
    """
    Initialization function to set up the intersecting participants list for each of the participant objects
    :param participants_dic: the full set of participants
    """
    for id_num, participant in participants_dic.items():
        for other_participant in participants.values():
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
        for other_participant in participants.values():
            if id_num == other_participant.id_num:  # skip self
                continue
            for s in participant.shares:
                if s in other_participant.shares:
                    l = participant.grouped_participants.get(s)
                    l.append(other_participant.id_num)
                    participant.grouped_participants[s] = l.copy()


def get_intersecting_shares(missing_shares, available_shares):
    """
    Helper function for getting intersecting shares between two lists
    :param missing_shares
    :param available_shares
    :return: list of intersecting shares
    """
    return list(set(missing_shares).intersection(set(available_shares)))


def random_participants(participant_dic, failed_participant, p_available, fault="Transient"):
    """
    Algorithm 1: Random Participants
    :param participant_dic: the full set of participants
    :param failed_participant: the participant whose share is being repaired
    :param p_available: availability probability
    :param fault: the fault model to be used
    :return: Boolean (whether repair was successful) and int (# of steps taken to repair aka # participants contacted)
    """
    faults = ["Permanent", "Transient"]
    assert fault in faults

    failed_participant.missing_shares = failed_participant.shares.copy()

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

        shares = get_intersecting_shares(failed_participant.missing_shares, P.shares)
        if shares:
            failed_participant.missing_shares.remove(shares[0])
        if not failed_participant.missing_shares:
            repaired = True
    return True, steps  # return True that repair was successful, will need a fail condd when using permanant fault


def stored_intersecting_participants(participant_dic, failed_participant, p_available, fault="Transient"):
    """
    Algorithm 2: Stored Intersecting Participants
    :param participant_dic: the full set of participants
    :param failed_participant: the participant whose share is being repaired
    :param p_available: availability probability
    :param fault: the fault model to be used
    :return: Boolean (whether repair was successful) and int (# of steps taken to repair aka # participants contacted)
    """
    faults = ["Permanent", "Transient"]
    assert fault in faults

    failed_participant.missing_shares = failed_participant.shares.copy()

    steps = 0
    return True, steps


"""
Test algorithm
"""
blocks = [[0, 1, 3], [0, 2, 6], [0, 4, 5], [1, 2, 4], [1, 5, 6], [2, 3, 5], [3, 4, 6]]
availability_probabilities = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
fault_model = "Transient"
participants = {}
num_iterations = 10000

# Instantiate participants, add to dict, initialize extra participant attributes
for i, block in enumerate(blocks):
    p = Participant(i, block)
    participants.update({i: p})
    init_intersecting_participants(participants)
    init_grouped_participants(participants)

# Iterate through availability probabilities: time repairs and count failed repairs at each probability
for prob in availability_probabilities:
    repair_wall_time = 0.0
    repair_process_time = 0.0
    failed_repairs = 0
    total_contacted = 0

    for i in range(num_iterations):

        participant_to_repair = participants.get((r.sample(participants.keys(), 1)[0]))

        start_wall_time = time.clock()
        start_process_time = time.process_time()
        success, participants_contacted = random_participants(participants, participant_to_repair, prob, fault_model)
        if success:
            repair_wall_time += (time.clock() - start_wall_time)
            repair_process_time += (time.process_time() - start_process_time)
            total_contacted += participants_contacted
        else:
            failed_repairs += 1

    success_repairs = num_iterations - failed_repairs
    avg_wall_time = repair_wall_time/success_repairs
    avg_process_time = repair_process_time/success_repairs
    avg_participants_contacted = total_contacted/success_repairs

    print("Availability probabilty: " + str(prob) + "\n" +
          "Failed repairs: " + str(failed_repairs) + "\n" +
          "Total wall clock time of " + str(repair_wall_time) + " with average of " + str(avg_wall_time) + " per repair\n" +
          "Total process time of " + str(repair_process_time) + " with average of " + str(avg_process_time) + " per repair\n"+
          "Total participants contacted during successful repairs: " + str(total_contacted) + "\n" +
          "Average participants contacted per successful repair:" + str(avg_participants_contacted))
    print("___________________________________________________________________________________________________________")

