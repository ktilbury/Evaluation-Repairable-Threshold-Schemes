#!/usr/bin/python3


class Participant:
    "Participant class for use in evaluating the repairable threshold algorithms."
    participant_count = 0

    def __init__(self, id_num, shares):
        self.id_num = id_num
        self.shares = shares
        self.missing_shares = None
        self.intersecting_participants = []  # This is the set R from algorithm 2
        self.grouped_participants = {}  # This is the set R from algorithm 3
        Participant.participant_count += 1


    def import_participants(design):
        participant_dic = {}
        # depends on how we encode the designs
        return participant_dic
