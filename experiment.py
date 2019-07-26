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
num_repair_iterations = 10000
repair_algos_list = [random_participants, stored_intersecting_participants, stored_grouped_participants]


# design (7, 7, 3, 3, 1)-BIBD, gives threshold of 2
design_blocks = [[0, 1, 3], [0, 2, 6], [0, 4, 5], [1, 2, 4], [1, 5, 6], [2, 3, 5], [3, 4, 6]]
data = evaluate_design(design_blocks, avail_probs, fault_models_list, num_repair_iterations, repair_algos_list)
data.to_csv("7,3,1-BIBD_sample_results.csv", encoding='utf-8', index=False)

# design (9, 12, 4, 3, 1)-BIBD
#          [,1] [,2] [,3]
# Block-1     1    4    7
# Block-2     1    5    8
# Block-3     3    5    7
# Block-4     7    8    9
# Block-5     1    6    9
# Block-6     4    5    6
# Block-7     3    4    9
# Block-8     3    6    8
# Block-9     2    5    9
# Block-10    2    4    8
# Block-11    1    2    3
# Block-12    2    6    7


# design (13, 13, 4, 4, 1)-BIBD
#          [,1] [,2] [,3] [,4]
# Block-1     1    3    5    7
# Block-2     7    9   11   13
# Block-3     7    8   10   12
# Block-4     1    6    9   10
# Block-5     5    6   11   12
# Block-6     1    4   12   13
# Block-7     4    5    8    9
# Block-8     3    4   10   11
# Block-9     2    5   10   13
# Block-10    3    6    8   13
# Block-11    2    4    6    7
# Block-12    2    3    9   12
# Block-13    1    2    8   11


# design (16, 20, 5, 4, 1)-BIBD
#          [,1] [,2] [,3] [,4]
# Block-1     1    2   14   16
# Block-2     3    6   12   13
# Block-3     4    6   11   16
# Block-4    10   12   15   16
# Block-5    10   11   13   14
# Block-6     1    3    7   11
# Block-7     1    4    9   12
# Block-8     8    9   11   15
# Block-9     7    9   13   16
# Block-10    1    5   13   15
# Block-11    1    6    8   10
# Block-12    7    8   12   14
# Block-13    5    6    9   14
# Block-14    4    5    7   10
# Block-15    3    5    8   16
# Block-16    3    4   14   15
# Block-17    2    6    7   15
# Block-18    2    5   11   12
# Block-19    2    4    8   13
# Block-20    2    3    9   10


# design (21, 21, 5, 5, 1)-BIBD
#          [,1] [,2] [,3] [,4] [,5]
# Block-1     3    5    8   10   11
# Block-2     3    6   12   17   21
# Block-3     1    2   11   12   13
# Block-4     2   10   14   17   18
# Block-5     4   11   14   16   21
# Block-6     1   10   15   20   21
# Block-7     2    5    9   19   21
# Block-8     8    9   12   14   15
# Block-9     2    6    8   16   20
# Block-10    7    9   11   17   20
# Block-11    7    8   13   18   21
# Block-12    1    5    6    7   14
# Block-13    4    6    9   10   13
# Block-14    4    5   12   18   20
# Block-15    2    3    4    7   15
# Block-16    6   11   15   18   19
# Block-17    3   13   14   19   20
# Block-18    5   13   15   16   17
# Block-19    7   10   12   16   19
# Block-20    1    4    8   17   19
# Block-21    1    3    9   16   18


# design (25, 30, 6, 5, 1)-BIBD, gives threshold of 2 or 3 depending on base scheme and repairing degree d of 5
#          [,1] [,2] [,3] [,4] [,5]
# Block-1    10   12   17   19   22
# Block-2     4   11   17   20   24
# Block-3     6    9   11   21   23
# Block-4     7   16   18   19   23
# Block-5     4    6    8   15   19
# Block-6     4    7   10   21   25
# Block-7     1   10   11   14   18
# Block-8     1   12   15   20   23
# Block-9     3   14   19   20   21
# Block-10    3    5   17   23   25
# Block-11   12   13   16   21   24
# Block-12    3    6   18   22   24
# Block-13   11   15   16   22   25
# Block-14    1    9   19   24   25
# Block-15    3    9   10   13   15
# Block-16    3    7    8   11   12
# Block-17    8    9   14   16   17
# Block-18    8   13   18   20   25
# Block-19    1    6    7   13   17
# Block-20    5    7   14   15   24
# Block-21    5    6   10   16   20
# Block-22    4    5    9   12   18
# Block-23    1    5    8   21   22
# Block-24    4   13   14   22   23
# Block-25    2    7    9   20   22
# Block-26    2    6   12   14   25
# Block-27    2    5   11   13   19
# Block-28    1    2    3    4   16
# Block-29    2    8   10   23   24
# Block-30    2   15   17   18   21


# design (31, 31, 6, 6, 1)-BIBD
#          [,1] [,2] [,3] [,4] [,5] [,6]
# Block-1     1    6    9   25   28   29
# Block-2     3    7   11   16   29   30
# Block-3     3    4    6   10   12   21
# Block-4     4    7    8   20   24   28
# Block-5     5    7   12   18   25   26
# Block-6    10   13   17   20   26   29
# Block-7     8   10   19   25   30   31
# Block-8    11   14   20   21   22   25
# Block-9    12   14   19   24   27   29
# Block-10    3   15   17   23   24   25
# Block-11   15   16   19   21   26   28
# Block-12   10   11   18   23   27   28
# Block-13    1    4   14   23   26   30
# Block-14    9   13   18   21   24   30
# Block-15    9   12   16   20   23   31
# Block-16    1    7   17   21   27   31
# Block-17    3    8    9   22   26   27
# Block-18    6    8   14   16   17   18
# Block-19    1    8   11   12   13   15
# Block-20    6    7   13   19   22   23
# Block-21    5    6   15   20   27   30
# Block-22    1    5   10   16   22   24
# Block-23    4    5    9   11   17   19
# Block-24    3    5   13   14   28   31
# Block-25    4   15   18   22   29   31
# Block-26    2    7    9   10   14   15
# Block-27    2    6   11   24   26   31
# Block-28    1    2    3   18   19   20
# Block-29    2    5    8   21   23   29
# Block-30    2    4   13   16   25   27
# Block-31    2   12   17   22   28   30
