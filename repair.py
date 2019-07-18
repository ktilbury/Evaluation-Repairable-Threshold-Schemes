#!/usr/bin/python3

from participant import Participant

import random as r
import time
import numpy as np


def get_shares(missing_shares, available_shares):
    return set(missing_shares).intersection(available_shares)


def random_participants(participant_dic, failed_participant, p_available, fault="Transient"):
    faults = ["Permanent", "Transient"]
    assert fault in faults

    failed_participant.missing_shares = failed_participant.shares

    steps = 0
    repaired = False
    while not repaired:
        P_id = np.random.choice(list(participant_dic))
        if P_id == failed_participant.id_num: # don't contact self
            continue

        P = participant_dic[P_id]
        steps += 1

        if fault == "Transient":
            if np.random.random_sample() > p_available:
                continue
        if fault == "Permanent":
            if P.availability is False:
                continue
            else:
                if np.random.random_sample() > p_available:
                    P.availability = False
                    continue        

        shares = get_shares(failed_participant.missing_shares, P.shares)
        if shares:
            failed_participant.missing_shares.remove(shares[0])
            if not missing_shares:
                repaired = True


# Test algorithm
blocks = [[0, 1, 3], [0, 2, 6], [0, 4, 5], [1, 2, 4], [1, 5, 6], [2, 3, 5], [3, 4, 6]]
availability_probabilities = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
participants = {}

for i, block in enumerate(blocks):
    p = Participant(i, block)
    participants.update({i: p})
