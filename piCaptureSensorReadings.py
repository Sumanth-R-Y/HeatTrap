#!/usr/bin/python
import os
import time
import sys


def mainprocess(filePrefix, deviceList, NumberofPoints = 10000, DelayBetweenPoints = 10, FlushCount = 100):
	
	# validation::::
	if NumberofPoints <= 0:
		print('Number of data points should be > 0. Taking default 10000\n')
		NumberofPoints = 10000
	if DelayBetweenPoints < 0:
		print('Delay or time between two points should be >= 0. Taking default 10\n')
		DelayBetweenPoints = 10
	elif DelayBetweenPoints > 100:
		print('A high delay was chosen between data points')
	
	if FlushCount <=0:
		print('FlushCount used in flushing the records to file should be >= 0. Taking default 100\n')
		FlushCount = 100
	
	
	# Create file pointer dict for each device
	# {'deviceid':'Correspondingfilepointer',...}

	# (i,open(filePrefix+i+".data",'w') - creates a tuple
	# The list comprehension creates list of above tuples
	# Then dict is applied on the list of tuples to get the above Dictionary

	fpDict = dict([(i,open(filePrefix+i+".data",'w')) for i in deviceList ])

	# Timeseries points to be written to a file Time.data
	# The following is a file pointer to Time.data
	TimeFileP = open(filePrefix+"Time.data","w")

	# Count variable to compare with FlushCount and 
	#  then perform flush
	count = 1

	# Based on Number of Points - the loop will be run
	for i in range(0,NumberofPoints):

		TimeFileP.write(str(time.time())+"\n")
		
		for j in deviceList:
			fpDict[j].writelines(str(gettemp(j))+"\n")
		
		if count % FlushCount == 0:
			[v.flush() for k,v in fpDict.items()]
			TimeFileP.flush()
		
		count=count+1
		
		print(i)
		if DelayBetweenPoints > 0 :
			time.sleep(DelayBetweenPoints)
	
	# close the file pointers
	[v.close() for k,v in fpDict.items()]
	TimeFileP.close()
	

		
def gettemp(id):
	#print(id)
	try:
		f = open('/sys/bus/w1/devices/' + id + '/w1_slave', 'r')
		#78 01 55 05 7f a5 a5 66 ed : crc=ed YES\n
		#78 01 55 05 7f a5 a5 66 ed t=23500\n
		
		line = f.readline()
		#78 01 55 05 7f a5 a5 66 ed : crc=ed YES\n

		crc = line.rsplit(' ',1)
		#['78 01 55 05 7f a5 a5 66 ed : crc=ed' 'YES\n']
		
		crc = crc[1].replace('\n','')
		#'YES'

		if crc == 'YES':
			line = f.readline()
			#78 01 55 05 7f a5 a5 66 ed t=23500\n

			TempCelsius = line.rsplit('t=',1)
			#['78 01 55 05 7f a5 a5 66 ed ' '23500\n']
			TempCelsius = TempCelsius[1].replace('\n','')

		else:
			# 6 9's tells that an issue with DS18B20 sensor CRC.
			TempCelsius=999999
		f.close()
		
		return int(TempCelsius)
		
	except:
		# 7 9's tells that an  exception in try block
		e = sys.exc_info()[0]
		print(sys.exc_info())
		print(e)
		return 9999999
		
if __name__ == '__main__':
	curdir = os.getcwd()
	print(curdir)

	# Raspberry pi - w1 enabled
	# /sys/bus/w1/devices
	devicelist = os.listdir('/sys/bus/w1/devices')
	print(devicelist)
	
	# w1_bus_master1' is not a device. Everything else treat it as device
	devicelist.remove('w1_bus_master1')
	print(devicelist)
	
	fileprefix = time.strftime('%Y%m%d%H%M%S',time.localtime())
	print(fileprefix)
	
	mainprocess(fileprefix,devicelist,NumberofPoints=10000,DelayBetweenPoints=0,FlushCount=1000)
	
	
	
