Labs for NLPIR, Spring 2013
===========================

Repo for the source code and other resources.

# Slides

Slides are under the **slides/** folder

# Course projects

All resources related to the course projects can be found under **course_projects/** folder. 

The folder **sts2012** contains a detailed readme (README.md) that explains how to run the baseline system step by step.

# Lab01

**NOTE**: if you import the project into Eclipse and you have JDK 6, you need to modify the classpath, since the project assumes you have JDK 7 installed. To change the JDK to ver. 6 you need to go to project properties and change the preferred JRE to your system default. 

The code works fine with JDK 6 as well.

## Running the code

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