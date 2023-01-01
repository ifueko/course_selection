#!/bin/bash

docker build -t openai_playground . && docker run -it --publish-all --rm --volume "/home/ifueko:/home/ifueko" --gpus all --net host --privileged --name openai_playground openai_playground
