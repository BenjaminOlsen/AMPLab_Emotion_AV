#!/usr/local/bin/python

import os
import json
import essentia
from essentia import Pool
from essentia.standard import (
    MonoLoader,
    TensorflowPredict,
    TensorflowPredictEffnetDiscogs,
    TensorflowPredictMusiCNN
)
print("SUCK ITTT")
# Model files for inference of embeddings and arousal/valence.
root_dir = "Emotion-AV-annotation-dataset"
essentia_path = os.path.join(root_dir, "essentia-models")
audio_dir = os.path.join(root_dir, "audio_chunks/audio.004/")
total_audio_cnt = 0

print(f"essentia_path: {essentia_path}")

all_audio_paths = []
for subdir, dirs, files in os.walk(audio_dir):
    for file in files:
        filepath = os.path.join(subdir, file)
        if file.endswith(".mp3"):
            total_audio_cnt += 1
            all_audio_paths.append(filepath)
        else:
            print("forgetting: {}".format(os.path.join(subdir, file)))

print(f"total_audio_cnt: {total_audio_cnt}")
#print(all_audio_paths)


# Transfer Learning Models
pb_models = {
    'deam-effnet': os.path.join(essentia_path, "deam-effnet-discogs-1/deam-effnet-discogs-1.pb"),
    'emo-effnet': os.path.join(essentia_path, "emomusic-effnet-discogs-1/emomusic-effnet-discogs-1.pb"),
    'deam-vggish': os.path.join(essentia_path, "deam-vggish-audioset-1/deam-vggish-audioset-1.pb"),
    'emo-vggish': os.path.join(essentia_path, "emomusic-vggish-audioset-1/emomusic-vggish-audioset-1.pb"),
    'deam-musicnn': os.path.join(essentia_path, "deam-musicnn-msd-1/deam-musicnn-msd-1.pb"),
    'emo-musicnn': os.path.join(essentia_path, "emomusic-musicnn-msd-1/emomusic-musicnn-msd-1.pb"),
}
# Embedding Models
embeddings = {
    'effnet': os.path.join(essentia_path, "effnet-discogs-1.pb"),
    'vggish': os.path.join(essentia_path, "audioset-vggish-3.pb"),
    'musicnn': os.path.join(essentia_path, "msd-musicnn-1.pb"),
}
# Metadata JSONs
metadatas = {
    'deam-effnet': os.path.join(essentia_path, "deam-effnet-discogs-1/deam-effnet-discogs-1.json"),
    'emo-effnet': os.path.join(essentia_path, "emomusic-effnet-discogs-1/emomusic-effnet-discogs-1.json"),
    'deam-vggish': os.path.join(essentia_path, "deam-vggish-audioset-1/deam-vggish-audioset-1.json"),
    'emo-vggish': os.path.join(essentia_path, "emomusic-vggish-audioset-1/emomusic-vggish-audioset-1.json"),
    'deam-musicnn': os.path.join(essentia_path, "deam-musicnn-msd-1/deam-musicnn-msd-1.json"),
    'emo-musicnn': os.path.join(essentia_path, "emomusic-musicnn-msd-1/emomusic-musicnn-msd-1.json"),
}


av_model_path = pb_models['deam-effnet']
embeddings_model_path = embeddings['effnet']
#I/O Layers
metadata = json.load(open(metadatas['deam-effnet'], "r"))


## Parameters for the Effnet embeddings
patch_size = 128
patch_hop_size = patch_size // 2
input_layer = "melspectrogram"
output_layer = "onnx_tf_prefix_BatchNormalization_496/add_1"

# Instantiate the embeddings model
print ("instantiating embeddings model")
embeddings_model = TensorflowPredictMusiCNN(
    graphFilename=embeddings_model_path,
    input=input_layer,
    output=output_layer,
    patchSize=patch_size,
    patchHopSize=patch_hop_size,
)

print( "instantiating AV model")
# Instantiate the arousal-valence model
av_input_layer = metadata["schema"]["inputs"][0]["name"]
av_output_layer = metadata["schema"]["outputs"][0]["name"]
av_model = TensorflowPredict(
    graphFilename=av_model_path,
    inputs=[av_input_layer],
    outputs=[av_output_layer],
)

###### EVALUATION:
print (" starting ")
print(f"total_audio_cnt: {total_audio_cnt}")
file_cnt = 0
prediction_dict = {}
for filepath in all_audio_paths:
    print("~~~~~~~~~~~~")
    if filepath.endswith(".mp3"):
        file_cnt += 1
        print(f"evaluating {filepath}: {file_cnt}/{total_audio_cnt}")
        audio = MonoLoader(filename=filepath, sampleRate=16000)()

        embeddings = embeddings_model(audio)
        feature = embeddings.reshape(-1, 1, 1, embeddings.shape[1])
        pool = Pool()
        pool.set(av_input_layer, feature)

        print(f"running av_model on {filepath}")
        predictions = av_model(pool)[av_output_layer].squeeze()

        print(f"prediction: {predictions.mean(axis=0)}")  # [valence, arousal]

        basename = os.path.basename(filepath)
        fn, ext = os.path.splitext(basename)
        prediction_dict[fn] = predictions.mean(axis=0).tolist()
    else:
        print(f"skipping {file}")

with open('predictions_deam-effnet.json', 'w') as f:
    json.dump(prediction_dict, f)
