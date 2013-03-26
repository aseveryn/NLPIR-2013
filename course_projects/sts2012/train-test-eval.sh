#! /bin/bash

model=$1

## Path to the SVM-Light-TK binaries
SVM=./SVM-Light-1.5-rer

## Path to the STS datasets
GOLD=datasets/gold/test
DATA=models/${model}

PARAMS="-z r -t 5 -C V"  # vector only

LEARN="${SVM}/svm_learn ${PARAMS}" 
CLASSIFY=${SVM}/svm_classify

echo "SVM-TK path: " ${SVM}

### Train
echo "Training"
cmd="${LEARN} ${DATA}/train/ALL.svmtk ${DATA}/svmtk.model"
echo ${cmd}
eval ${cmd}

### Test
test_datasets="MSRpar MSRvid SMTeuroparl OnWN SMTnews"
for test in ${test_datasets}; do
	echo "Classifying " $test
	cmd="${CLASSIFY} ${DATA}/test/${test}.svmtk ${DATA}/svmtk.model ${DATA}/test/${test}.pred"
	echo ${cmd}
	eval ${cmd}
done

### Eval

# remove temporary files
rm -rf /tmp/all.pred /tmp/all.gs

for test in ${test_datasets}; do
	echo "Evaluating " $test
	python postprocess_scores.py ${DATA}/test/${test}.svmtk ${DATA}/test/${test}.pred
	./correlation.pl ${DATA}/test/${test}.pred ${GOLD}/STS.gs.${test}.txt
	cat ${DATA}/test/${test}.pred >> /tmp/all.pred
	cat ${GOLD}/STS.gs.${test}.txt >> /tmp/all.gs
done

echo "All"
./correlation.pl /tmp/all.pred /tmp/all.gs

# remove temporary files
rm -rf /tmp/all.pred /tmp/all.gs
