#!/usr/bin/env bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
DATA_DIR=$(readlink -m $DIR/../lti_app/core/data)

wget https://www.languagetool.org/download/LanguageTool-stable.zip -P $DATA_DIR
unzip $DATA_DIR/LanguageTool-stable.zip -d $DATA_DIR
rm $DATA_DIR/LanguageTool-stable.zip
mv $(readlink -m "$DATA_DIR/LanguageTool-*") $DATA_DIR/languagetool
