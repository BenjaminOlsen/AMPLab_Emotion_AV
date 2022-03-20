#!/usr/local/bin/python
import os
import json
from math import inf

### read spotify annotations
annotation_dir = 'self_annotations'
total_annot_cnt = 0
all_annot_paths = []
av_dict = {}
for subdir, dirs, files in os.walk(annotation_dir):
    for file in files:
        filepath = os.path.join(subdir, file)
        if file.endswith(".json"):
            total_annot_cnt += 1
            all_annot_paths.append(filepath)
        else:
            print("forgetting: {}".format(os.path.join(subdir, file)))

print(f"found {total_annot_cnt} self annotations")

av_dict = {}
parse_cnt = 0

for filepath in all_annot_paths:
    basename = os.path.basename(filepath)
    fn, ext = os.path.splitext(basename)
    print(f"basename: {basename}, fn: {fn}, ext: {ext}")
    with open(filepath, 'r') as f:
        data = json.load(f)
        hashes = fn.split('-')
        a_name = hashes[3]
        b_name = hashes[4]
        higher_arousal = data['higher_arousal']
        higher_valence = data['higher_valence']
        parse_cnt += 1

        if higher_arousal == 'a':
            higher_arousal_name = a_name
            lower_arousal_name = b_name
            a_arous = 1
            arous_char = '>'
        elif higher_arousal == 'b':
            higher_arousal_name = b_name
            lower_arousal_name = a_name
            a_arous = -1
            arous_char = '<'
        elif higher_arousal == 'not_selected':
            higher_arousal_name = a_name
            lower_arousal_name = b_name
            a_arous = inf
            arous_char = '?'
        else: # equivalent
            higher_arousal_name = a_name
            lower_arousal_name = b_name
            a_arous = 0
            arous_char = '=='

        if higher_valence == 'a':
            higher_valence_name = a_name
            lower_valence_name = b_name
            a_valence = 1
            val_char = '>'
        elif higher_valence == 'b':
            higher_valence_name = b_name
            lower_valence_name = a_name
            a_valence = inf
            val_char = '<'
        elif higher_valence == 'not_selected':
            higher_arousal_name = a_name
            lower_arousal_name = b_name
            a_valence = -inf
            val_char = '?'
        else:
            higher_valence_name = b_name
            lower_valence_name = a_name
            a_valence = 0
            val_char = '=='

        #av_list.append({'valence': [a_name, val_char, b_name], 'arousal': [a_name, arous_char, b_name]})
        print (f"{a_name} vs {b_name}")

        if a_name not in av_dict:
            print(f"inserting {a_name}")
            av_dict[a_name] = {}
        if b_name not in av_dict[a_name]:
            print(f"inserting[{a_name}][{b_name}]")
            av_dict[a_name][b_name] = {}

        #if b_name not in av_dict:
        #    print(f"inserting {a_name}")
        #    av_dict[b_name] = {}
        #if a_name not in av_dict[b_name]:
        #    print(f"inserting[{b_name}][{a_name}]")
        #    av_dict[b_name][a_name] = {}

        try:
            av_dict[a_name][b_name]['arousal'] = a_arous
            av_dict[a_name][b_name]['valence'] = a_valence
        #    av_dict[b_name][a_name]['arousal'] = -a_arous
        #    av_dict[b_name][a_name]['valence'] = -a_valence
            print("~~~~~~~~~")
            print("a {} - v {} / a {} - v {}".format(av_dict[a_name][b_name]['arousal'], av_dict[a_name][b_name]['valence'], av_dict[b_name][a_name]['arousal'], av_dict[b_name][a_name]['valence']))
        except Exception as e:
            print ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! wtf: {}".format(e))

        ### now, in av_dict, given two filenames, you can do:
        ### av_dict[f1][f2]['arousal' / 'valence'] ==
        # { 1 if f1 > f2,
        #  -1 if f1 < f2,
        #   0 if f1 == f2,
        #   +/- inf if N/A }
    f.close()
print("##################### {}/{}: arousal: [{}]: {} {} {}; valence: [{}]: {} {} {}".format(parse_cnt, total_annot_cnt, higher_arousal, a_name, arous_char, b_name, higher_valence, a_name, val_char, b_name))

with open('annotation_summary_self.json', 'w') as f:
    json.dump(av_dict, f)
