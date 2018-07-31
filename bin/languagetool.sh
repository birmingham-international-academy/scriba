#!/usr/bin/env bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
DATA_DIR=$(readlink -m $DIR/../lti_app/core/data)

echo "> Downloading LanguageTool..."
wget https://www.languagetool.org/download/LanguageTool-stable.zip -P $DATA_DIR
echo "> Extracting LanguageTool..."
unzip $DATA_DIR/LanguageTool-stable.zip -d $DATA_DIR
rm $DATA_DIR/LanguageTool-stable.zip
mv $(readlink -m "$DATA_DIR/LanguageTool-*") $DATA_DIR/languagetool
echo "> The files have been saved in $DATA_DIR/languagetool"
