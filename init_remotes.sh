#!/bin/bash

# define gtri and skai remotes
# NOTE: relies on
# - ssh key auth for gtri_remote
# - gh auth using personal token for skai_remote

# remove if exists
git remote rm origin
git remote rm skai_remote
git remote rm gtri_remote

# add remotes
git remote add skai_remote https://github.com/skAIVision/skai-ai-message-interface.git
git remote add gtri_remote ssh://git@eoslbitbucket.eosl.gtri.org:7999/adat/skai-ai-message-interface.git

# set defaults
git fetch skai_remote
git checkout main
git branch --set-upstream-to=skai_remote/main main

# define aliases
git config alias.fetch-skai "fetch skai_remote"
git config alias.fetch-gtri "fetch gtri_remote"
git config alias.push-skai "push skai_remote"
git config alias.push-gtri "push gtri_remote"
