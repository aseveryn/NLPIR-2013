Labs for NLPIR, Spring 2013
===========================

Repo for the source code and other resources.

# Lab01

* Compile code:

`sh run_compile.sh`

* Run simple demo:

`sh run_hello.sh`

* Index data from QA:

`sh run_qa_index.sh indexdir data/answers.50k.txt`

* Interactive searching

Play with interactive searching querying the indexed QA data. 
Supply the path to the folder with Lucene index, e.g. **index** 
and maximum documents to retrieve per query, e.g. **10**:

`sh run_qa_interactive.sh index 10`