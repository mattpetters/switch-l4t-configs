#!/bin/bash

for DIR in $(find .  -mindepth 1 -maxdepth 1 -type d -not -path '*/\.*')
do
	VERSION=$(cat $DIR/VERSION)
	tar -czvf "$DIR-$VERSION.tar.gz" -C $DIR .
done
