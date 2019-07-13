#!/usr/bin/python3


class Participant:
    "Participant class for use in evaluating the repairable threshold algorithms."
    participant_count = 0

    def __init__(self, id_num, share, availability, repair_candidates):
        self.id_num = id_num
        self.share = share
        self.availability = availability
        self.repair_candidates = repair_candidates  # This is the set R from algorithm 3
        Participant.participant_count += 1


