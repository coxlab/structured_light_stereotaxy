#!/bin/bash

DIR=$1

if [ -z "$DIR" ]; then
    echo "No directory specified"
    exit 1
fi

pushd $DIR
## rename all jpgs
#echo "renaming jpgs"
#for f in `find ./$DIR -name *.jpg`; do
#    echo "moving $f to ${f%.jpg}.png"
#    mv "$f" "${f%.jpg}.png"
#done

# check that all files exist
echo "checking scan directories `find . -name "Scan*"`"
for d in `find . -name "Scan*"`; do
    echo "checking scan directory $d"
    # rename (fixing case and extension)
    for f in skull ref; do
        if [ ! -f "$d/$f.obj" ]; then
            find $d/ -iname "$f.obj" -exec mv "{}" "$d/$f.obj" \;
        fi
        if [ ! -f "$d/$f.png" ]; then
            find $d/ -iname "$f.[jp][pn]g" -exec mv "{}" "$d/$f.png" \;
        fi
        # check if files exist
        for e in png obj; do
            if [ ! -f "$d/$f.$e" ]; then
                echo "File $d/$f.$e not found"
                exit 1
            fi
        done
    done
    # simply skull.obj
    pushd $d
    echo "============================================="
    echo "======= Please save to: $d/skull.obj"
    echo "===== Uncheck all EXCEPT Vert: texcoord"
    echo "============================================="
    meshlab skull.obj &> /dev/null
    popd
done

popd
