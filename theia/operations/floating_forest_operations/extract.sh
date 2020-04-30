#!/bin/bash

rm -rf temp/L* && find temp/archives/*.gz | xargs basename -s .tar.gz | xargs -P 4 -I {} sh -c 'echo Extracting {}; mkdir temp/{}; tar -xzf temp/archives/{}.tar.gz -C temp/{};'
