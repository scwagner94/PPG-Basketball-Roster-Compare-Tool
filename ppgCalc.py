import time,csv
from multiprocessing import Process, Manager

#GLOBALS
salaryDict = {} #{PlayerString,Salary}
ppgDict = {} #{PlayerString,PPG}
positionDict = {} #{PlayerString,PositionString}
allPlayersList = [] #[PlayerStrings]
PGList = [] #only pg
SGList = [] #only sg
SFList = [] #only sf
PFList = [] #only pf
CList = [] #only c
GList = [] #only pg or sg
FList = [] #only sf or pf
UTIList = [] #any position
ignoreQuestionable = True
salaryCap = 50000
outputFileName = "outputResults.txt"
rosterFileName = "input4.csv"
start_time = time.time()
outputFile = open(outputFileName,'w')
print "BEGINNING ROSTER CALCULATION\n\n\n\n"
outputFile.write("BEGINNING ROSTER CALCULATION\n\n\n\n")
#special class to store the best roster
class roster:
	def __init__(self,PG,SG,SF,PF,C,G,F,UTIL):
		self.pg = PG
		self.sg = SG
		self.sf = SF
		self.pf = PF
		self.c = C
		self.g = G
		self.f = F
		self.util = UTIL
	
	def calcPPG(self):
		global ppgDict
		pgPoints = ppgDict[self.pg]
		sgPoints = ppgDict[self.sg]
		sfPoints = ppgDict[self.sf]
		pfPoints = ppgDict[self.pf]
		cPoints = ppgDict[self.c]
		gPoints = ppgDict[self.g]
		fPoints = ppgDict[self.f]
		uPoints = ppgDict[self.util]
		sum = pgPoints + sgPoints + sfPoints + pfPoints + cPoints + gPoints + fPoints + uPoints
		return sum
	
	def calcSalary(self):
		global salaryDict
		pgPoints = salaryDict[self.pg]
		sgPoints = salaryDict[self.sg]
		sfPoints = salaryDict[self.sf]
		pfPoints = salaryDict[self.pf]
		cPoints = salaryDict[self.c]
		gPoints = salaryDict[self.g]
		fPoints = salaryDict[self.f]
		uPoints = salaryDict[self.util]
		sum = pgPoints + sgPoints + sfPoints + pfPoints + cPoints + gPoints + fPoints + uPoints
		return sum

#reads input file of players
def readDB():
	global salaryDict, ppgDict, positionDict, allPlayersList, rosterFileName
	f = open(rosterFileName, 'rt')
	k = 0
	try:
		reader = csv.reader(f)
		for row in reader:
			position = row[0]
			status = row[1]
			name = row[2]
			salary = int(row[3])
			ppg = float(row[4])
			if status != "" and ignoreQuestionable:
				continue
			salaryDict[name] = salary
			ppgDict[name] = ppg
			positionDict[name] = position
			allPlayersList.append(name)
	finally:
		f.close()

#loads the dictionaries and lists with relevant players
def loadGloablPlayerDicts():
	global positionDict,PGList,SGList,SFList,PFList,CList,GList,FList,UTIList
	for key,value in positionDict.iteritems(): #key:name value:position
		if value == "PG":
			PGList.append(key)
			GList.append(key)
			UTIList.append(key)
		elif value == "SG":
			SGList.append(key)
			GList.append(key)
			UTIList.append(key)
		elif value == "SF":
			SFList.append(key)
			FList.append(key)
			UTIList.append(key)
		elif value == "PF":
			PFList.append(key)
			FList.append(key)
			UTIList.append(key)
		elif value == "C":
			CList.append(key)
			UTIList.append(key)
		else:
			print "ERROR",key,value
	
#runs the actual method and finds best roster for one PG, adds to shared memory
def doWork(currentPG,SGList,SFList,PFList,CList,GList,FList,UTIList,salaryCap,returnDict):
	cBestRoster = None
	#first, remove currentPG from G and UTIL lists
	for cSG in SGList:
		cSFList = list(SFList)
		for cSF in cSFList:
			cPFList = list(PFList)
			for cPF in cPFList:
				cCList = list(CList)
				for cC in cCList:
					cGList = list(GList)
					cGList.remove(currentPG)
					cGList.remove(cSG)
					for cG in cGList:
						cFList = list(FList)
						cFList.remove(cSF)
						cFList.remove(cPF)
						for cF in cFList:
							cUtilList = list(UTIList)
							cUtilList.remove(currentPG)
							cUtilList.remove(cSG)
							cUtilList.remove(cSF)
							cUtilList.remove(cPF)
							cUtilList.remove(cC)
							cUtilList.remove(cG)
							cUtilList.remove(cF)
							for cUtil in cUtilList:
								cRoster = roster(currentPG,cSG,cSF,cPF,cC,cG,cF,cUtil)
								cSalary = cRoster.calcSalary()
								if cSalary > salaryCap:
									continue
								else:
									cPPG = cRoster.calcPPG()
									if cBestRoster == None:
										cBestRoster = cRoster
									elif cBestRoster.calcPPG() < cRoster.calcPPG():
										cBestRoster = cRoster
	returnDict.append(cBestRoster)
								
		
##START MAIN PROGRAM
#setup dependencies
readDB()
loadGloablPlayerDicts()
bestRoster = None

#create shared memory location for threads
manager = Manager()
returnRosterList = manager.list()

#begin thread execution, expectes a returned list of roster type...
processes = []
for current in PGList:
	newProc = Process(target=doWork, args=(current,SGList,SFList,PFList,CList,GList,FList,UTIList,salaryCap,returnRosterList))
	processes.append(newProc)
	
for proc in processes:
	proc.start()
for proc in processes:
	proc.join()

potentialBestRosters = returnRosterList
#finds best roster from all the rosters
for currentRoster in potentialBestRosters:
	currentRosterPPG = currentRoster.calcPPG()
	if bestRoster == None:
		bestRoster = currentRoster
	elif bestRoster.calcPPG() < currentRoster.calcPPG():
		bestRoster = currentRoster


#prints the best roster and relevant information at end of program
print "\n\n\n"
outputFile.write("\n\n\n")
print "BEST ROSTER CALCULATION:\n"
outputFile.write("BEST ROSTER CALCULATION:\n")
print "\tPlayer\t\tPoints\tSalary"
outputFile.write("\tPlayer\t\tPoints\tSalary")
outputFile.write("\n")
print "PG:",bestRoster.pg,"\t",ppgDict[bestRoster.pg],"\t",salaryDict[bestRoster.pg]
outputFile.write("PG:")
outputFile.write(str(bestRoster.pg))
outputFile.write("\t")
outputFile.write(str(ppgDict[bestRoster.pg]))
outputFile.write("\t")
outputFile.write(str(salaryDict[bestRoster.pg]))
outputFile.write("\n")
print "SG:",bestRoster.sg,"\t",ppgDict[bestRoster.sg],"\t",salaryDict[bestRoster.sg]
outputFile.write("SG:")
outputFile.write(str(bestRoster.sg))
outputFile.write("\t")
outputFile.write(str(ppgDict[bestRoster.sg]))
outputFile.write("\t")
outputFile.write(str(salaryDict[bestRoster.sg]))
outputFile.write("\n")
print "SF:",bestRoster.sf,"\t",ppgDict[bestRoster.sf],"\t",salaryDict[bestRoster.sf]
outputFile.write("SF:")
outputFile.write(bestRoster.sf)
outputFile.write("\t")
outputFile.write(str(ppgDict[bestRoster.sf]))
outputFile.write("\t")
outputFile.write(str(salaryDict[bestRoster.sf]))
outputFile.write("\n")
print "PF:",bestRoster.pf,"\t",ppgDict[bestRoster.pf],"\t",salaryDict[bestRoster.pf]
outputFile.write("PF:")
outputFile.write(bestRoster.pf)
outputFile.write("\t")
outputFile.write(str(ppgDict[bestRoster.pf]))
outputFile.write("\t")
outputFile.write(str(salaryDict[bestRoster.pf]))
outputFile.write("\n")
print " C:",bestRoster.c,"\t",ppgDict[bestRoster.c],"\t",salaryDict[bestRoster.c]
outputFile.write(" C:")
outputFile.write(bestRoster.c)
outputFile.write("\t")
outputFile.write(str(ppgDict[bestRoster.c]))
outputFile.write("\t")
outputFile.write(str(salaryDict[bestRoster.c]))
outputFile.write("\n")
print " G:",bestRoster.g,"\t",ppgDict[bestRoster.g],"\t",salaryDict[bestRoster.g]
outputFile.write(" G:")
outputFile.write(bestRoster.g)
outputFile.write("\t")
outputFile.write(str(ppgDict[bestRoster.g]))
outputFile.write("\t")
outputFile.write(str(salaryDict[bestRoster.g]))
outputFile.write("\n")
print " F:",bestRoster.f,"\t",ppgDict[bestRoster.f],"\t",salaryDict[bestRoster.f]
outputFile.write(" F:")
outputFile.write(bestRoster.f)
outputFile.write("\t")
outputFile.write(str(ppgDict[bestRoster.f]))
outputFile.write("\t")
outputFile.write(str(salaryDict[bestRoster.f]))
outputFile.write("\n")
print "UT:",bestRoster.util,"\t",ppgDict[bestRoster.util],"\t",salaryDict[bestRoster.util]
outputFile.write("UT:")
outputFile.write(bestRoster.util)
outputFile.write("\t")
outputFile.write(str(ppgDict[bestRoster.util]))
outputFile.write("\t")
outputFile.write(str(salaryDict[bestRoster.util]))
outputFile.write("\n")
print "\n"
outputFile.write("\n")
print "Total PPG Estimated: ",bestRoster.calcPPG()
outputFile.write("Total PPG Estimated: ")
outputFile.write(str(bestRoster.calcPPG()))
outputFile.write("\n")
print "       Total Salary: ",bestRoster.calcSalary()
outputFile.write("       Total Salary: ")
outputFile.write(str(bestRoster.calcSalary()))
outputFile.write("\n")
print "\n\n\ndone\n\n"
outputFile.write("\n\n\ndone\n\n")
print("--- %s seconds ---" % (time.time() - start_time))
timeToPrint = time.time() - start_time
outputFile.write("seconds: ")
outputFile.write(str(timeToPrint))
outputFile.close()
