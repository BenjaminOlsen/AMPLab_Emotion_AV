import json
import os
import math

EQUIVALENT_THRESHOLD = 0.02 #FIXME
PREDICTION_DIR = 'predictions/3'
PRINT_DEBUG = False

################################################################################
########### remove inconsisent triplets from pairwise relative annotations:
################ if A > B && B > C && A < C
################ if A < B && B < C && A > C
def remove_inconsistent_triplets(annotations_self):

    for a in annotations_self:
        for b in annotations_self[a]:
            arousal_ab = annotations_self[a][b]['arousal']
            valence_ab = annotations_self[a][b]['valence']
            for c in annotations_self[a]:
                if b != c and b in annotations_self:
                    if c in annotations_self[b]:
                        # a,b; b,c; a,c:
                        arousal_ac = annotations_self[a][c]['arousal']
                        valence_ac = annotations_self[a][c]['valence']

                        arousal_bc = annotations_self[b][c]['arousal']
                        valence_bc = annotations_self[b][c]['valence']
                        if PRINT_DEBUG:
                            print(f"[remove_inconsistent_triplets]: inspecting a: {a}, b: {b}, c: {c}")
                elif c != b and c in annotations_self:
                    if b in annotations_self[c]:
                        # a,b; a,c; c,b
                        arousal_ac = annotations_self[a][c]['arousal']
                        valence_ac = annotations_self[a][c]['valence']

                        arousal_bc = -annotations_self[c][b]['arousal']
                        valence_bc = -annotations_self[c][b]['valence']
                        if PRINT_DEBUG:
                            print(f"[remove_inconsistent_triplets]: inspecting a: {a}, b: {b}, c: {c}")
                else:
                    continue

                # if there is inconsistency, mark each as inf to ignore!
                if valence_ab == valence_bc and valence_ab != valence_ac:
                    if PRINT_DEBUG:
                        print(f"[inconsistency] - valence: removing [{a}][{b}], [{a}][{c}],[{b}][{c}]")
                    annotations_self[a][b]['valence'] = math.inf
                    annotations_self[a][c]['valence'] = math.inf
                    if b in annotations_self and c in annotations_self[b]:
                        annotations_self[b][c]['valence'] = math.inf
                    elif c in annotations_self and b in annotations_self[c]:
                        annotations_self[c][b]['valence'] = math.inf
                    else:
                        print(f"[inconsistency] - ABSURDDDD error with inconsistncies: a: {a}, b: {b}, c: {c}")

                if arousal_ab == arousal_bc and arousal_ab != arousal_ac:

                    print(f"[inconsistency] - arousal: removing [{a}][{b}], [{a}][{c}],[{b}][{c}]")
                    annotations_self[a][b]['arousal'] = math.inf
                    annotations_self[a][c]['arousal'] = math.inf
                    if b in annotations_self and c in annotations_self[b]:
                        annotations_self[b][c]['arousal'] = math.inf
                    elif c in annotations_self and b in annotations_self[c]:
                        annotations_self[c][b]['arousal'] = math.inf
                    else:
                        print(f"[inconsistency] - ABSURDDDD error with inconsistncies: a: {a}, b: {b}, c: {c}")
    return annotations_self

def do_compare_annotations(remove_inconsistencies = False):
    # read self annotations:
    with open('annotation_summary_self.json', 'r') as f:
        try:
            annotations_self = json.load(f)
        except Exception as e:
            print("problem loading self annotations: {}".format(e))
    ### for two filename (track_ids) f1, f2:
    ### annotations_self[f1][f2]['arousal' / 'valence'] ==
    # { 1 if f1 > f2,
    #  -1 if f1 < f2,
    #   0 if f1 == f2,
    #   +/- inf if N/A }

    if remove_inconsistencies:
        print("REMOVING INCONSISTENCIES")
        annotations_self = remove_inconsistent_triplets(annotations_self)

    ##############################
    # read spotify annotations:
    with open('annotation_summary_spotify.json', 'r') as f:
        try:
            annotations_spotify = json.load(f)
        except Exception as e:
            print("problem loading spotify annotations: {}".format(e))

    ####### format:
    ######  annotations_spotify[track_id]['valence' / 'arousal']
    #print(annotations_spotify)

    ######################################
    # read the arousal - valence calculations from each model:

    prediction_paths = []
    for subdir, dirs, files in os.walk(PREDICTION_DIR):
        for file in files:
            filepath = os.path.join(subdir, file)
            if file.endswith(".json"):
                prediction_paths.append(filepath)
            else:
                print("forgetting: {}".format(os.path.join(subdir, file)))

    ### each prediction file:
    ### dict[track_id][0] - valence;
    ### dict[track_id][1] - arousal


    def compare_with_ground_truth(annotations_self, prediction_data, is_spotify = False):
        # iterate through self annotations,
        # find corresponding predicted arousal/valence pairs.
        # see if they agree

        valence_cnt = 0
        arousal_cnt = 0
        valence_agree_cnt = 0
        arousal_agree_cnt = 0
        valence_omit_cnt = 0
        arousal_omit_cnt = 0
        equal_arousal_cnt = 0
        equal_valence_cnt = 0

        for a_name in annotations_self:
            for b_name in annotations_self[a_name]:
                prediction_a = prediction_data[a_name]
                prediction_b = prediction_data[b_name]

                relative_arousal = annotations_self[a_name][b_name]['arousal']
                relative_valence = annotations_self[a_name][b_name]['valence']

                #############################
                # valence

                if is_spotify:
                    predicted_valence_diff = prediction_a['valence'] - prediction_b['valence']
                else:
                    # valid for model predictions only!
                    predicted_valence_diff = prediction_a[0] - prediction_b[0]

                if abs(predicted_valence_diff) < EQUIVALENT_THRESHOLD:
                    equal_valence_cnt += 1


                omit_valence = False
                if math.isinf(relative_valence): # skip unanswered
                    if PRINT_DEBUG:
                        print("[valence]: skipping {} - {}: valence {}".format(a_name, b_name, relative_valence))
                    omit_valence = True
                    valence_omit_cnt += 1
                elif ( relative_arousal == 1 and predicted_valence_diff > EQUIVALENT_THRESHOLD
                    or relative_arousal == 0 and abs(predicted_valence_diff) < EQUIVALENT_THRESHOLD
                    or relative_arousal == -1 and predicted_valence_diff < -EQUIVALENT_THRESHOLD):
                    agree_valence = True
                    valence_agree_cnt += 1
                    if PRINT_DEBUG:
                        print(f"[valence]: AGREE    {valence_agree_cnt}: diff: {predicted_valence_diff:.4f} ({a_name} - {b_name})")
                else:
                    agree_valence = False
                    if PRINT_DEBUG:
                        print(f"[valence]: DISAGREE {valence_cnt + 1 - valence_agree_cnt}: diff: {predicted_valence_diff:.4f} ({a_name} - {b_name})")
                if not omit_valence:
                    valence_cnt += 1

                #############################
                # arousal
                if is_spotify:
                    predicted_arousal_diff = prediction_a['arousal'] - prediction_b['arousal']
                else:
                    # valid for model predictions only!
                    predicted_arousal_diff = prediction_a[1] - prediction_b[1]

                if abs(predicted_arousal_diff) < EQUIVALENT_THRESHOLD:
                    equal_arousal_cnt += 1

                omit_arousal = False
                if math.isinf(relative_arousal): # skip unanswered
                    if PRINT_DEBUG:
                        print("[arousal]: skipping {} - {}: arousal {}".format(a_name, b_name, relative_arousal))
                    omit_arousal = True
                    arousal_omit_cnt += 1
                elif ( relative_arousal == 1 and predicted_arousal_diff > EQUIVALENT_THRESHOLD
                    or relative_arousal == 0 and abs(predicted_arousal_diff) < EQUIVALENT_THRESHOLD
                    or relative_arousal == -1 and predicted_arousal_diff < -EQUIVALENT_THRESHOLD):
                    agree_arousal = True
                    arousal_agree_cnt += 1
                    if PRINT_DEBUG:
                        print(f"[arousal]: AGREE    {arousal_agree_cnt}: diff: {predicted_arousal_diff:.4f} ({a_name} - {b_name})")
                else:
                    agree_arousal = False
                    if PRINT_DEBUG:
                        print(f"[arousal]: DISAGREE {arousal_cnt + 1 - arousal_agree_cnt}: diff: {predicted_arousal_diff:.4f} ({a_name} - {b_name})")

                if not omit_arousal:
                    arousal_cnt += 1

        print(f"equal valence: {equal_valence_cnt}; equal arousal: {equal_arousal_cnt}; threshold: {EQUIVALENT_THRESHOLD}")
        return arousal_agree_cnt, arousal_omit_cnt, arousal_cnt, \
               valence_agree_cnt, valence_omit_cnt, valence_cnt



    ############################################################
    ################# MODEL PREDICTIONS ########################
    ############################################################
    comparison = {}
    print("arousal")
    for filepath in prediction_paths:
        with open(filepath, 'r') as f:
            prediction_data = json.load(f)
            basename = os.path.basename(filepath)
            fn, ext = os.path.splitext(basename)

            arousal_agree_cnt, arousal_omit_cnt, \
                arousal_cnt, valence_agree_cnt, \
                valence_omit_cnt, valence_cnt = compare_with_ground_truth(annotations_self, prediction_data)

            agree_rate_arousal = arousal_agree_cnt / arousal_cnt
            agree_rate_valence = valence_agree_cnt / valence_cnt
            #print(f"~~~~~~~~~~~~\n{fn}:\n-- arousal: agree {arousal_agree_cnt}/{arousal_cnt} = {agree_rate_arousal:.2f} (omitted {arousal_omit_cnt})\n-- valence: agree {valence_agree_cnt}/{valence_cnt} = {agree_rate_valence:.2f} (omitted {valence_omit_cnt})")
            print(f"{fn}, {arousal_agree_cnt}, {arousal_cnt}, {agree_rate_arousal:.2f},{arousal_omit_cnt}")

    print("valence")
    for filepath in prediction_paths:
        with open(filepath, 'r') as f:
            prediction_data = json.load(f)
            basename = os.path.basename(filepath)
            fn, ext = os.path.splitext(basename)

            arousal_agree_cnt, arousal_omit_cnt, \
                arousal_cnt, valence_agree_cnt, \
                valence_omit_cnt, valence_cnt = compare_with_ground_truth(annotations_self, prediction_data)

            agree_rate_arousal = arousal_agree_cnt / arousal_cnt
            agree_rate_valence = valence_agree_cnt / valence_cnt
            #print(f"~~~~~~~~~~~~\n{fn}:\n-- arousal: agree {arousal_agree_cnt}/{arousal_cnt} = {agree_rate_arousal:.2f} (omitted {arousal_omit_cnt})\n-- valence: agree {valence_agree_cnt}/{valence_cnt} = {agree_rate_valence:.2f} (omitted {valence_omit_cnt})")
            print(f"{fn}, {valence_agree_cnt},{valence_cnt},{agree_rate_valence:.2f},{valence_omit_cnt}")

    ############################################################
    ############## SPOTIFY ANNOTATIONS #########################
    ############################################################
    arousal_agree_cnt, arousal_omit_cnt, \
        arousal_cnt, valence_agree_cnt, \
        valence_omit_cnt, valence_cnt = compare_with_ground_truth(annotations_self, annotations_spotify, is_spotify = True)

    agree_rate_arousal = arousal_agree_cnt / arousal_cnt
    agree_rate_valence = valence_agree_cnt / valence_cnt
    #print(f"~~~~~~~~~~~~\nspotify!:\n-- arousal: accuracy {arousal_agree_cnt}/{arousal_cnt} = {agree_rate_arousal:.2f} (omitted {arousal_omit_cnt})\n-- valence: accuracy {valence_agree_cnt}/{valence_cnt} = {agree_rate_valence:.2f} (omitted {valence_omit_cnt})")
    print(f"~~~~~~~~~~~~\nspotify!:\n-- arousal: accuracy \n {arousal_agree_cnt}, {arousal_cnt}, {agree_rate_arousal:.2f},{arousal_omit_cnt}\n-- valence: accuracy \n {valence_agree_cnt},{valence_cnt},{agree_rate_valence:.2f},{valence_omit_cnt}")
    return annotations_self


if __name__ == '__main__':
    do_compare_annotations(False)
    do_compare_annotations(True)
