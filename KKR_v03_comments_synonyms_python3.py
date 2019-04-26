import re
import zlib
import os
import random

# Реализуем NCD приближение-метрики
def NCD(x,y):
	# Сжимаем строку x и находим длину сжатой версии
	Cx = zlib.compress(x)
	Cx_len = len(Cx)
	# Сжимаем строку y и находим длину сжатой версии
	Cy = zlib.compress(y)
	Cy_len = len(Cy)
 
 	# конкатенируем строки x и y, сжимаем их и находим длину
	xy = x + y
	Cxy = zlib.compress(xy)
	Cxy_len = len(Cxy)

	# рассчитываем искомое расстояние по NCD формуле
	distance = float( Cxy_len - min(Cx_len, Cy_len)) / max(Cx_len, Cy_len)

	return distance

# получаем списков всех файлов, находящихся в указанной директории (dirName)
def getFileList(dirName):
	names = os.listdir(dirName)
	fileList = []
	for name in names:
		fullname = os.path.join(dirName, name)
		if os.path.isfile(fullname):
			fileList.append(fullname)

	return fileList

# создаем массив длины len псевдо-случайных чисел в диапазоне от 0 до maxVal
def createRandomIndexList(maxVal, len):
	if maxVal < len:
		return -1
	if maxVal == len:
		return range(0, maxVal - 1)
	randomList = []
	for i in range(0, len):
		randomVal = random.randint(0, maxVal - 1)
		while randomVal in randomList: 
			randomVal = random.randint(0, maxVal - 1)

		randomList.append(randomVal)
	return randomList


# классифицируем текст testFileText на основе файлов-экземпляров из категории спама (spamExamples)
# и обыкновенных писем (legalExamples)
# для сравнения используем по count образцов
def classifyText(testFileText, spamExamples, legalExamples, count):
	# находим количество файлов образцов в каждой категории
	spamExamplesLen  = len(spamExamples)
	legalExamplesLen = len(legalExamples)

	# создаем псевдо-случайные массивы с номерами файлов для сравнения
	legalIndexes  = createRandomIndexList(legalExamplesLen, count)
	spamIndexes  = createRandomIndexList(spamExamplesLen, count)

	# заводим переменные для хранения средней длины до каждой категории
	averageDistanceToSpam = 0.0
	averageDistanceToLegal = 0.0

	# находим среднее расстояние от нашего классифицируемого текста  
	# до обыкновенных писем
	for i in legalIndexes:
		legalFileHandler = open(legalExamples[i])
		legalFileRawText = legalFileHandler.readlines()[0].encode()

		averageDistanceToLegal += NCD(testFileText, legalFileRawText)
	averageDistanceToLegal /= count
	
	# находим среднее расстояние от нашего классифицируемого текста  
	# до спам писем
	for i in spamIndexes:
		spamFileHandler = open(spamExamples[i])
		spamFileRawText = spamFileHandler.readlines()[0].encode()

		averageDistanceToSpam += NCD(testFileText, spamFileRawText)
	averageDistanceToSpam /= count
	
	# находим наименьшее расстояние и возвращаем ту категории, к файлам-представилям которой оно было найдено
	if (averageDistanceToSpam < averageDistanceToLegal):
		return "Spam"
	else:
		return "Legal"

# классифицируем все файлы, подготовленные к классификации (testSpamFiles, testLegalFiles)
# для удобства тестируемые фалйы были размещены в две директории
# для сравнения используем письма образцы -spamFiles и legalFiles и проводим coutOfComparsion сравнений
def classifyLetters(spamFiles, legalFiles, testSpamFiles, testLegalFiles, coutOfComparsion):
	# находим количество файлов образцов в каждой категории
	legalFilesLen = len(legalFiles)
	spamFilesLen = len(spamFiles)

	# создаем псевдо-случайные массивы с номерами файлов для сравнения
	legalIndexes  = createRandomIndexList(legalFilesLen, 5)
	spamIndexes  = createRandomIndexList(spamFilesLen, 5)

	# создаем переменную для хранения точности классификатора на спам письмах
	spamTestPrecision = 0.0

	# для всех тестовых писем, которые ДОЛЖНЫ быть классифицированы как спам
	for testFile in testSpamFiles:
		# открываем файл и считываем содержимое пиьсма
		testFileHandler = open(testFile)
		testFileRawText = testFileHandler.readlines()[0].encode()

		# сохраняем результат работы классификатора на данном тексте
		predictedClass = classifyText(testFileRawText, spamFiles, legalFiles, coutOfComparsion)

		# сравниваем полученный класс с реальным
		# если ответ верный, т.е. классы совпали, то увеличиваем счетчик правильных ответов
		if predictedClass == "Spam":
			spamTestPrecision += 1

	# находим процент правильных классификаций спам писем
	spamTestPrecision = float(spamTestPrecision) / len(testSpamFiles)
	
	# создаем переменную для хранения точности классификатора на легальных письмах
	legalTestPrecision = 0.0
	
	# для всех тестовых писем, которые ДОЛЖНЫ быть классифицированы как обыкновенным
	for testFile in testLegalFiles:
		# открываем файл и считываем содержимое пиьсма
		testFileHandler = open(testFile)
		testFileRawText = testFileHandler.readlines()[0].encode()
		
		# сохраняем результат работы классификатора на данном тексте
		predictedClass = classifyText(testFileRawText, spamFiles, legalFiles, coutOfComparsion)

		# если ответ верный, т.е. классы совпали, то увеличиваем счетчик правильных ответов
		if predictedClass == "Legal":
			legalTestPrecision += 1
		
	# находим процент правильных классификаций обыкновенных писем	
	legalTestPrecision = float(legalTestPrecision) / len(testLegalFiles)

	# возвращаем список, составленный из точности классификации спама и обыкновенных писем
	return [spamTestPrecision, legalTestPrecision]

# запоминаем директории, в которых хранятся образцы обыкновенных и спам писем
# и письма, предназначенные для классификации
legalDir = 'D:\\lingspam_public\\mainFolder\\synonymFolder\\legal'
legalFiles = getFileList(legalDir)

spamDir = 'D:\\lingspam_public\\mainFolder\\synonymFolder\\spam'
spamFiles = getFileList(spamDir)

testSpamDir = 'D:\\lingspam_public\\mainFolder\\synonymFolder\\testFolder\\spamTest'
testSpamFiles = getFileList(testSpamDir)

testLegalDir = 'D:\\lingspam_public\\mainFolder\\synonymFolder\\testFolder\\legalTest'
testLegalFiles = getFileList(testLegalDir)


# перебирая параметр, отвечающий за количество избираемых документов для классификации, 
# находим процент правильных ответов классификатора
precisionCountTest = []
for compCount in range(0,210,10):
	precisionCountTest.append(classifyLetters(spamFiles, legalFiles, testSpamFiles, testLegalFiles, compCount))
print (precisionCountTest)

