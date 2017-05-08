# this script searches duckduckgo for R packages so we can quickly categorize if the package is a 
# CRAN, bioconductor, github or other package
# creates some nice output
import duckduckgo,time


fname = "./r-libs.txt"

with open(fname) as fp:
    for line in fp:
       # this "dummy request" avoids the problem but i dunno why
       # see https://github.com/mikejs/python-duckduckgo/issues/3 
       duckduckgo.query("foo")
       content = line.strip() + " R"
       search_result = duckduckgo.get_zci(content)
       print content + "\t" + search_result
       time.sleep(10)


