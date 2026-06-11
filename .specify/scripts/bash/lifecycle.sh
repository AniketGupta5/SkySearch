#!/bin/bash
# SkySearch — Dev Lifecycle Scripts

case "$1" in
  install)
    echo "Installing dependencies..."
    pip install -r requirements.txt
    ;;
  run)
    echo "Starting SkySearch..."
    streamlit run app.py
    ;;
  push)
    REMOTE=${2:-origin}
    echo "Pushing to $REMOTE..."
    git add -A
    git commit -m "${3:-chore: update}"
    git push $REMOTE main
    ;;
  *)
    echo "Usage: ./lifecycle.sh [install|run|push <remote> <message>]"
    ;;
esac
