## AMPLab Jupyter notebook with Essentia and Tensorflow

This notebook is provided for the 2020-2022 AMPLab courses, for the assignments
issued for the Large-scale Music Processing module.
It is designed to provide a fast-to-use environment with jupyter notebook and essentia
pre-installed.
You can also use [google colab](https://colab.research.google.com/) instead of this image for the task.


### Usage

Clone this repository

    git clone https://github.com/MTG/amplab-jamendo-notebook.git

Start the server

    docker-compose up

Access the notebook server at http://localhost:8888. The password to access the notebook is 'mir'



OR just run locally in this docker container, the command is in
    start_bash_in_docker.zsh

then run the scripts:
    ./emo_effnet.py
    ./emo_musicnn.py
    ./emo_vggish.py
    ./deam_effnet.py
    ./deam_musicnn.py
    ./deam_vggish.py

sloppy but effective

to run the annotation comparison
