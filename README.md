# Build Docker images from R projects 
this repo contains tools/scripts to build Docker images from existing R applications or shiny web applications

## A. build dockerfile R package installation commands to install R packages from cran/bioconductor/github source
PLEASE NOTE THAT THIS SCRIPT DOES NOT TAKE CARE OF VERSION NUMBERING OF THE PACKAGES SO 
ALWAYS THE LATEST VERSIONS ARE EXPECTED!!!

IF YOU NEED TO SETTLE VERSION NUMBERS GOTO 
STEP "B. build dockerfile R package installation commands from sessionInfo file"


First goto existing R/shiny project of choice, exec following lines
these lines do not only include packages using library() lines but also find additional packages based on function calls 

because I have seen people calling functions from their static package name without importing a library line: e.g. d3heatmap::scale()

```bash
find <path to R project> -iname "*.[rR]" -exec grep "library(" {} \; | grep -v "#" | sort | uniq |sed 's/^library(\([a-zA-Z0-9\.]*\))$/\1/g' > ./r-debs-tmp.txt
find <path to R project> -iname "*.[rR]" -exec grep -o "[0-9a-zA-Z]*::[0-9a-zA-Z]*(" {} \; | grep  -o "^[0-9a-zA-Z]*" |  sort | uniq > ./r-debs-tmp2.txt
cat r-debs-tmp.txt r-debs-tmp2.txt | sort | uniq > ./r-debs.txt
```
for example
```bash
find ../../../caR-devel/caRpools_devel/ -iname "*.[rR]" -exec grep "library(" {} \; | grep -v "#" | sort | uniq | sed 's/^library(\([a-zA-Z0-9\.]*\))$/\1/g' > ./r-debs-tmp.txt
find ../../../caR-devel/caRpools_devel/ -iname "*.[rR]" -exec grep -o "[0-9a-zA-Z_-]*::[0-9a-zA-Z_-]*(" {} \; | grep  -o "^[0-9a-zA-Z]*" |  sort | uniq > ./r-debs-tmp2.txt
 cat r-debs-tmp.txt r-debs-tmp2.txt | sort | uniq > ./r-debs.txt
```

reformat to look better
```bash
sed 's/^library(\([a-zA-Z0-9\.]*\))$/\1/g' r-debs.txt > r-libs.txt
```
query a search engine to differentiate between cran, bioconductor or git etc. sources for the packages

```bash
python get-search-engine-hits.py r-libs.txt > r-packages-sources.txt 
```

manually edit the result file manually because search engine results are not 100% accurate, e.g. crayon top result is http://www.gamezebo.com/2011/06/26/super-crayon-review/ but this does not give information about R package, do manual search and replace with "crayon R cran" so it is parsable later
edit r-packages-sources.txt after making a copy of it first
```bash
cp r-packages-sources.txt r-packages-sources-accurate.txt
vi r-packages-sources-accurate.txt
```

next build R dependency part for dockerfile
```bash
python build-dep-list-docker.py > final.txt
```
example output will look like
```
RUN R -e 'packages.to.install.r <- c("caTools","data.table","dplyr","DT","ggplot2","highcharter","httr","jsonlite","MESS","openxlsx","reshape2","seqinr","shiny","shinyBS","shinydashboard","shinyjs","sm","tidyr","VennDiagram","gmailr"); install.packages(packages.to.install.r,repos="http://cran.rstudio.com/")'
RUN R -e  'packages.to.install.bioconductor <-  c("BiocGenerics","BiocParallel","biomaRt","DESeq2","Rqc","ShortRead");source("http://bioconductor.org/biocLite.R");biocLite();biocLite(packages.to.install.bioconductor)'
RUN R -e  'devtools::install_github("ScreenBEAM")';
```
put the output of ```final.txt``` into your dockerfile of choice
DONE!

## B. build dockerfile R package installation commands from sessionInfo file

this script creates all-in-one dependency resolution strings for R projects to be used in Dockerfiles or pure command line
useful for dockerizations of R / shiny projects in production environments


The ```build-dep-list-docker.py``` script takes three parametes from which two are input files:

param 1: a file generated by the output of the following bash commands done in a R project folder to resolve all included libraries
this line does not only include packages using library() lines but also finds additional packages based on function calls 
-- some functions are called with their static package name without a library line before: e.g. d3heatmap::scale()

```bash
find <path to R project> -iname "*.[rR]" -exec grep "library(" {} \; | grep -v "#" | sort | uniq |sed 's/^library(\([a-zA-Z0-9\.]*\))$/\1/g' > ./r-debs-tmp.txt
find <path to R project> -iname "*.[rR]" -exec grep -o "[0-9a-zA-Z]*::[0-9a-zA-Z]*(" {} \; | grep  -o "^[0-9a-zA-Z]*" |  sort | uniq > ./r-debs-tmp2.txt
cat r-debs-tmp.txt r-debs-tmp2.txt | sort | uniq > ./r-debs.txt
```
For example
```bash
find ../../../caR-devel/caRpools_devel/ -iname "*.[rR]" -exec grep "library(" {} \; | grep -v "#" | sort | uniq | sed 's/^library(\([a-zA-Z0-9\.]*\))$/\1/g' > ./r-debs-tmp.txt
find ../../../caR-devel/caRpools_devel/ -iname "*.[rR]" -exec grep -o "[0-9a-zA-Z_-]*::[0-9a-zA-Z_-]*(" {} \; | grep  -o "^[0-9a-zA-Z]*" |  sort | uniq > ./r-debs-tmp2.txt
 cat r-debs-tmp.txt r-debs-tmp2.txt | sort | uniq > ./r-debs.txt
```

param 2: a file generated by the following R command (you need to make sure that this R version can run your R application you want to dockerize)
to get exact versions of all our R packages along their source of installation (e.g. github.com, CRAN, Bioconductor)
remember, you can dockerize everything, in our example we use a shiny webapp
first load all packages you will need for this app, then use devtools::source_info()

```bash
awk '{print "library("$1")"}' ./r-debs.txt > /tmp/libs.R; echo "devtools::session_info();" >> /tmp/libs.R;
R -e 'source("/tmp/libs.R")' > sessionInfo.txt
```

param 3: the name of the repo where the dep can be found, or if you have stored all dependencies locally you can also use a file path to your deps

```bash
python build-dep-list-docker.py r-debs.txt sessionInfo.txt "http://cloud.r-project.org/"

```
or
```
python build-dep-list-docker.py r-debs.txt sessionInfo.txt "file:///tmp/std_repo" 
```

put the output from standard out into a Dockerfile of choice

TODO: adjust the script of step A. to grab package version numbers from
the CRAN web page (maybe there is a CRAN API?)
