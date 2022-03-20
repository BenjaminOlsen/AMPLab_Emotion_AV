import json
import os
import math

EQUIVALENT_THRESHOLD = 0.05 #FIXME

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

# read spotify annotations:
with open('annotation_summary_spotify.json', 'r') as f:
    try:
        annotations_spotify = json.load(f)
    except Exception as e:
        print("problem loading spotify annotations: {}".format(e))
#######
######  annotations_spotify[track_id]['valence' / 'arousal']
#print(annotations_spotify)
# read the arousal - valence calculations from each model:

prediction_paths = []
for subdir, dirs, files in os.walk('predictions/1'):
    for file in files:
        filepath = os.path.join(subdir, file)
        if file.endswith(".json"):
            prediction_paths.append(filepath)
        else:
            print("forgetting: {}".format(os.path.join(subdir, file)))

### each prediction file:
### dict[track_id][0] - valence;
### dict[track_id][1] - arousal

PRINT_DEBUG = False

############################################################
############## SPOTIFY ANNOTATIONS #########################
############################################################
#for a_name in annotations_self:
#    for b_name in annotations_self[a_name]:
#        prediction_a = prediction_data[a_name]
#        prediction_b = prediction_data[b_name]

#        relative_arousal = annotations_self[a_name][b_name]['arousal']
#        relative_valence = annotations_self[a_name][b_name]['valence']

#        spotify_arousal_a = annotations_spotify[a_name]['arousal']
#        spotify_arousal_b = annotations_spotify[b_name]['arousal']
#        spotify_valence_a = annotations_spotify[a_name]['valence']
#        spotify_valence_b = annotations_spotify[b_name]['valence']

############################################################
################# MODEL PREDICTIONS ########################
############################################################
comparison = {}
for filepath in prediction_paths:
    with open(filepath, 'r') as f:
        prediction_data = json.load(f)
        basename = os.path.basename(filepath)
        fn, ext = os.path.splitext(basename)



        # iterate through self annotations,
        # find corresponding predicted arousal/valence pairs.
        # see if they agree
        valence_cnt = 0
        arousal_cnt = 0
        valence_agree_cnt = 0
        arousal_agree_cnt = 0
        valence_omit_cnt = 0
        arousal_omit_cnt = 0
        for a_name in annotations_self:
            for b_name in annotations_self[a_name]:
                prediction_a = prediction_data[a_name]
                prediction_b = prediction_data[b_name]

                relative_arousal = annotations_self[a_name][b_name]['arousal']
                relative_valence = annotations_self[a_name][b_name]['valence']


                #############################
                # valence
                predicted_valence_diff = prediction_a[0] - prediction_b[0]

                if math.isinf(relative_valence): # skip unanswered
                    if PRINT_DEBUG:
                        print("[valence]: skipping {} - {}".format(a_name, b_name))
                    valence_omit_cnt += 1
                    continue
                elif ( relative_arousal == 1 and predicted_valence_diff > EQUIVALENT_THRESHOLD
                    or relative_arousal == 0 and abs(predicted_valence_diff) < EQUIVALENT_THRESHOLD
                    or relative_arousal == -1 and predicted_valence_diff > -EQUIVALENT_THRESHOLD):
                    agree_valence = True
                    valence_agree_cnt += 1
                    if PRINT_DEBUG:
                        print(f"[valence]: AGREE    {valence_agree_cnt}: diff: {predicted_valence_diff:.4f} ({a_name} - {b_name})")
                else:
                    agree_valence = False
                    if PRINT_DEBUG:
                        print(f"[valence]: DISAGREE {valence_cnt + 1 - valence_agree_cnt}: diff: {predicted_valence_diff:.4f} ({a_name} - {b_name})")
                valence_cnt += 1

                #############################
                # arousal
                predicted_arousal_diff = prediction_a[1] - prediction_b[1]

                if math.isinf(relative_arousal): # skip unanswered
                    if PRINT_DEBUG:
                        print("[arousal]: skipping {} - {}".format(a_name, b_name))
                    arousal_omit_cnt += 1
                    continue
                elif ( relative_arousal == 1 and predicted_arousal_diff > EQUIVALENT_THRESHOLD
                    or relative_arousal == 0 and abs(predicted_arousal_diff) < EQUIVALENT_THRESHOLD
                    or relative_arousal == -1 and predicted_arousal_diff > -EQUIVALENT_THRESHOLD):
                    agree_arousal = True
                    arousal_agree_cnt += 1
                    if PRINT_DEBUG:
                        print(f"[arousal]: AGREE    {arousal_agree_cnt}: diff: {predicted_arousal_diff:.4f} ({a_name} - {b_name})")
                else:
                    agree_arousal = False
                    if PRINT_DEBUG:
                        print(f"[arousal]: DISAGREE {arousal_cnt + 1 - arousal_agree_cnt}: diff: {predicted_arousal_diff:.4f} ({a_name} - {b_name})")

                arousal_cnt += 1

        agree_rate_arousal = arousal_agree_cnt / arousal_cnt
        agree_rate_valence = valence_agree_cnt / valence_cnt
        print(f"~~~~~~~~~~~~\n{fn}:\n-- arousal: agree {arousal_agree_cnt}/{arousal_cnt} = {agree_rate_arousal:.2f} (omitted {arousal_omit_cnt})\n-- valence: agree {valence_agree_cnt}/{valence_cnt} = {agree_rate_valence:.2f} (omitted {valence_omit_cnt})")
