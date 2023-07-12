#! /bin/bash
# run analysis on cs and cel folders
echo "get includes"
python cs-analyse.py $CRYSTAL/include/ $CRYSTAL/include/bindings/cspace.i  -include > crystalincludes.txt
python cs-analyse.py $CEL/include/ $CEL/plugins/behaviourlayer/python/blcel.i -include -I$CRYSTAL/include > celincludes.txt

echo "get attributes"
python cs-analyse.py $CRYSTAL/include/ $CRYSTAL/include/bindings/cspace.i > crystalattributes.i
python cs-analyse.py $CEL/include/ $CEL/plugins/behaviourlayer/python/blcel.i > celattributes.i -I/home/caedes/SVN/CS//include

echo "python modules"
python cs-analyse.py $CRYSTAL/include/ $CRYSTAL/include/bindings/cspace.i -pymod > csproperties.py
python cs-analyse.py $CEL/include/ $CEL/plugins/behaviourlayer/python/blcel.i -pymod > celproperties.py
