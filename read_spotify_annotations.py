#!/usr/local/bin/python
import os
import json
import yaml
from yaml.loader import BaseLoader

### read spotify annotations
spotify_annotation_dir = 'Emotion-AV-annotation-dataset/annotations-spotifyapi_chunks/annotations-spotifyapi.004/'
total_annot_cnt = 0
all_annot_paths = []
av_dict = {}
for subdir, dirs, files in os.walk(spotify_annotation_dir):
    for file in files:
        filepath = os.path.join(subdir, file)
        if file.endswith(".yaml"):
            total_annot_cnt += 1
            all_annot_paths.append(filepath)
        else:
            print("forgetting: {}".format(os.path.join(subdir, file)))

print(f"found {total_annot_cnt} annotations")

# SLOW!
def get_arousal_valence(yamlPath):
    with open(yamlPath, 'r') as f:
        # slow:¡, bettr to scan file line per line?
        data = yaml.load(f, Loader=BaseLoader)
        arousal = ''
        valence  = ''
        try:
            arousal = data['audio_features']['energy']
            valence = data['audio_features']['valence']
        except Exception as e:
            print("problem reading yaml: {}".format(e.args))
        f.close()
        return arousal, valence

## FAST
def get_arousal_valence_fast(yamlPath):
    with open(yamlPath, 'r') as f:
        got_valence = False
        got_arousal = False
        for line in f:
            if 'energy' in line:
                try:
                    arousal = float(line.split(':')[1])
                    got_arousal = True
                except Exception as e:
                    print("problem reading energy: {}".format(e.args))
            elif 'valence' in line:
                try:
                    valence = float(line.split(':')[1])
                    got_valence = True
                except Exception as e:
                    print("problem reading energy: {}".format(e.args))
            if got_valence and got_arousal:
                break

        return arousal, valence

av_dict = {}
parse_cnt = 0
for filepath in all_annot_paths:
    basename = os.path.basename(filepath)
    fn, ext = os.path.splitext(basename)

    a, v = get_arousal_valence_fast(filepath)
    av_dict[fn] = {'valence': v, 'arousal': a}
    parse_cnt += 1
    print("{}/{}: got a: {}, v: {} from {}".format(parse_cnt, total_annot_cnt, a, v, basename))

with open('annotation_summary_spotify.json', 'w') as f:
    json.dump(av_dict, f)
print(av_dict)
