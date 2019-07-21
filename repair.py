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

    missing_shares = failed_participant.shares.copy()

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
        shares = get_intersecting_shares(missing_shares, P.shares)
        if shares:
            missing_shares.remove(shares[0])

        # Check if repair is successful
        if not missing_shares:
            # repaired = True
            return True, steps  # return True that repair was successful, and steps (ie # of participants contacted)


def stored_intersecting_participants(participant_dic, failed_participant, p_available, fault="Transient"):
    """
    Algorithm 2: Stored Intersecting Participants
    :param participant_dic: the dictionary of participants with failed_participant removed (as to not contact self)
    :param failed_participant: the participant object whose share is being repaired
    :param p_available: availability probability
    :param fault: the fault model to be used {"Permanent", "Transient"}
    :return: Boolean (whether repair was successful) and int (# of steps taken to repair aka # participants contacted)
    """
    faults = ["Permanent", "Transient"]
    assert fault in faults

    missing_shares = failed_participant.shares.copy()
    intersecting_participants = failed_participant.intersecting_participants.copy()

    steps = 0
    repaired = False
    while not repaired:
        # Select random participant from the set of intersecting participants:
        P_id = np.random.choice(intersecting_participants)
        P = participant_dic[P_id]

        steps += 1
        # See if the participant is available
        if fault == "Transient":
            if np.random.random_sample() > p_available:
                continue
        elif fault == "Permanent":
            if np.random.random_sample() > p_available:
                intersecting_participants.remove(P_id)  # remove from the list and don't consider contacting again
                if not intersecting_participants:  # if no more participants to try contacting, repair has failed
                    return False, steps
                continue

        # Request values for any of the subshares still needing to be repaired
        shares = get_intersecting_shares(missing_shares, P.shares)
        if shares:
            missing_shares.remove(shares[0])

        # Check if repair is successful
        if not missing_shares:
            # repaired = True
            return True, steps  # return True that repair was successful, and steps (ie # of participants contacted)


def stored_grouped_participants(participant_dic, failed_participant, p_available, fault="Transient"):
    """
    Algorithm 3: Stored Grouped Participants
    :param participant_dic: the dictionary of participants with failed_participant removed (as to not contact self)
    :param failed_participant: the participant object whose share is being repaired
    :param p_available: availability probability
    :param fault: the fault model to be used {"Permanent", "Transient"}
    :return: Boolean (whether repair was successful) and int (# of steps taken to repair aka # participants contacted)
    """
    faults = ["Permanent", "Transient"]
    assert fault in faults

    missing_shares = failed_participant.shares.copy()
    grouped_participants = failed_participant.grouped_participants.copy()

    steps = 0
    for s in missing_shares:
        repaired = False
        s_repair_candidates = grouped_participants.get(s)

        while not repaired and s_repair_candidates:
            # Select random participant from the set of repair candidates for this subshare s:
            P_id = np.random.choice(s_repair_candidates)

            steps += 1
            # See if the participant is available
            if fault == "Transient":
                if np.random.random_sample() > p_available:
                    continue
            elif fault == "Permanent":
                if np.random.random_sample() > p_available:
                    s_repair_candidates.remove(P_id)  # remove from the list and don't consider contacting again
                    continue

            # Since available, share s is repaired
            repaired = True

        if not repaired:
            return False, steps

    return True, steps
