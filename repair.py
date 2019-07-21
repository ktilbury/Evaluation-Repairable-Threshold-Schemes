#!/usr/bin/python3

from participant import Participant
import numpy as np


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
    :param participant_dic: the dictionary of participants with failed_participant removed (as to not contact self)
    :param failed_participant: the participant object whose share is being repaired
    :param p_available: availability probability
    :param fault: the fault model to be used {"Permanent", "Transient"}
    :return: Boolean (whether repair was successful) and int (# of steps taken to repair aka # participants contacted)
    """
    faults = ["Permanent", "Transient"]
    assert fault in faults

    failed_participant.missing_shares = failed_participant.shares.copy()

    steps = 0
    repaired = False
    while not repaired:
        # Select random participant:
        P_id = np.random.choice(list(participant_dic))
        P = participant_dic[P_id]

        steps += 1
        # See if the participant is available
        if fault == "Transient":
            if np.random.random_sample() > p_available:
                continue
        elif fault == "Permanent":
            if np.random.random_sample() > p_available:
                participant_dic.pop(P_id)  # remove from the dict and don't consider contacting again
                if not participant_dic:  # if there are no more participants to try contacting, repair has failed
                    return False, steps
                continue

        # Request values for any of the subshares needing to be repaired
        shares = get_intersecting_shares(failed_participant.missing_shares, P.shares)
        if shares:
            failed_participant.missing_shares.remove(shares[0])

        # Check if repair is successful
        if not failed_participant.missing_shares:
            # repaired = True
            return True, steps  # return True that repair was successful, and steps (ie # of participants contacted)


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

    # if shares:
    #     failed_participant.missing_shares.remove(shares[0])
    # if not failed_participant.missing_shares:
    #     # repaired = True
    #     return True, steps  # return True that repair was successful, and steps (ie # of participants contacted)
    # elif steps >= 1000000:
    #     return False, steps  # return False that repair unsuccessful after arbitrarily large number of steps




