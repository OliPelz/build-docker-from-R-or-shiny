# this script sorts all deps from r-packages-sources.txt file and generates cran, git and bioconductor install package commands

import re


fname = "./r-packages-sources-accurate.txt"

cran = []
bioconductor = []
github = []

with open(fname) as fp:
    for line in fp:
       words = line.strip().split()
       package = words[0]
       itsR    = words[1]
       type    = words[2]

       if not itsR == "R":
	print "no valid package line containg R"
        quit()
       if re.search("cran", type):
         cran.append(package)         
       elif re.search("bioconductor", type):
         bioconductor.append(package)
       elif re.search("github", type):
         m = re.match("https://github.com/([\/\w]+)", type)
         if m:
          github.append(m.group(1))
       else:
         print "no valid package type cran|bioconductor|github found for package " + package + ", bailing out..."
         quit()


# packages from cran

cranString = ','.join('"{0}"'.format(w) for w in cran)
# devtools::install_version(cran$package[i], version = cran$version[i], repos ="http://cran.us.r-project.org") 
print "RUN R -e 'packages.to.install.r <- c(\"devtools\"," + cranString + "); install.packages(packages.to.install.r,repos=\"http://cran.rstudio.com/\")'"

# packages from bioconductor

bioconductorString = ','.join('"{0}"'.format(w) for w in bioconductor)
print "RUN R -e  'packages.to.install.bioconductor <-  c(" + bioconductorString + ");source(\"http://bioconductor.org/biocLite.R\");biocLite();biocLite(packages.to.install.bioconductor)'"

# packages from github
 
githubString = ';'.join('devtools::install_github("{0}")'.format(w) for w in github)
if not githubString == "":
  print "RUN R -e  '" + githubString + "';"
