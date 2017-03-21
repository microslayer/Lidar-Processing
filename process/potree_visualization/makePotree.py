import sys
from subprocess import call

if (len(sys.argv) < 3): 
	print "Syntax: makePotree.py inputSource outputFolder outputName"
	sys.exit(1); 
		
inputSource = sys.argv[1]
outputFolder = sys.argv[2]
outputName = sys.argv[3]

command = "PotreeConverter.exe %s -o %s -p %s -s 1.0 -l 3 --output-format LAS" % (inputSource, outputFolder, outputName);
call(command);

htmlSitePath = "%s\\examples\\%s.html" % (outputFolder, outputName) 
print "\nmakePotree finished. Your file is %s" % htmlSitePath 