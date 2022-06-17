#!/bin/bash

# add remotes to be sure
git remote add skai_remote https://github.com/skAIVision/skai-ai-message-interface.git
git remote add gtri_remote ssh://git@eoslbitbucket.eosl.gtri.org:7999/adat/skai-ai-message-interface.git

echo ""
echo "================================"
echo "trying to push to skai remote..."
echo "================================"
git push skai_remote
echo ""
echo "================================"
echo "trying to push to gtri remote..."
echo "================================"
git push gtri_remote --force
echo ""