#!/bin/csh -f 

SVM_FOLDER=$1

SVM_HOME="course_projects/sts2012/SVM-Light-1.5-rer"

PARAMS="-t 5 -C V -j 5"  # pointwise reranker
# PARAMS="-t 5 -C V -V R"  # pairwise reranker (feature vector only)
# PARAMS="-t 5 -F 3 -C + -W R -V R"  # pairwise reranker (tree + feature vector)

PARAMS_STR=`echo ${PARAMS} | tr ' ' '_'`
model=svm.model.${PARAMS_STR}

cmd="./${SVM_HOME}/svm_learn ${PARAMS} ${SVM_FOLDER}/svm.train ${SVM_FOLDER}/${model}"
echo $cmd
eval $cmd

cmd="./${SVM_HOME}/svm_classify ${SVM_FOLDER}/svm.test ${SVM_FOLDER}/${model} ${SVM_FOLDER}/svm.pred"
echo $cmd
eval $cmd

cmd="python scripts/ev.py -f trec ${SVM_FOLDER}/svm.relevancy ${SVM_FOLDER}/svm.pred"
echo $cmd
eval $cmd
