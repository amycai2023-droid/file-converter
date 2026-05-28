#!/bin/bash
# Keep serveo tunnel alive. Launchd restarts this if it dies.
exec ssh -o StrictHostKeyChecking=no \
         -o ServerAliveInterval=60 \
         -o ServerAliveCountMax=3 \
         -o ExitOnForwardFailure=yes \
         -R 80:localhost:8000 serveo.net
