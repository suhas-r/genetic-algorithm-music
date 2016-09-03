import random
import xlrd
import pyglet
import time

iterations = 30
mutationRate = .03
crossoverRate = .8
sampleSize = 10
data = None #the excel file
genSize = 30
generation = []
database = [] #each combination corresponds to index 0-168 and holds list of notes
              #index 0 - 80 and holds rhythms
bestNotes = []
bestRhythms = []

#----------------GENETIC ALGORITHM---------------------#
class Individual:
    bestChromosome = None
    bestFitness = 0
    def __init__(self, chromosome, maxElement):
        self.chromosome = chromosome
        fitness = 0
        for i in range(0, maxElement * maxElement):
            #compare each value to the frequency in database
            #print("chrom")
            #print(chromosome[i])
            freq = 0
            for j in database[i]:
                if j == chromosome[i]:
                    freq = freq + 1
            fitness = fitness + freq / len(database[i])
            #print(freq)
        self.fitness = fitness
        if fitness > Individual.bestFitness:
            Individual.bestChromosome = chromosome
            Individual.bestFitness = fitness
    def getFitness (self):
        return self.fitness
    def getChromosome (self):
        return self.chromosome
    def setChromosome(self, newChrom):
        self.chromosome = newChrom
def randomChrom(maxElement):
    chrom = []
    for i in range (0, maxElement * maxElement):
        chrom.append(random.randint(0, maxElement - 1))
    return chrom
def createDatabase(startDatabase, endDatabase, maxElement):
    global database
    global data
    #notes
    for column in range (startDatabase, endDatabase, 3):
        #find number of rows in each column
        rowSize = 0
        i = 0
        while (i < data.nrows and data.cell(i, column).value != ''):
            rowSize = rowSize + 1
            i = i + 1
        for row in range (2, rowSize - 2):
            if maxElement == 13:
                index = notes_numbs(row, column) * maxElement + notes_numbs(row + 1, column)
                database[index].append(notes_numbs(row + 2, column))
            else:
                index = int(data.cell(row, column).value) * maxElement + int(data.cell(row + 1, column).value)
                database[index].append(int(data.cell(row + 2, column).value))
def notes_numbs(row, column):
    global data
    switcher = {
        "A": 1,
        "A#": 2,
        "B": 3,
        "C": 4,
        "C#": 5,
        "D": 6,
        "D#": 7,
        "E": 8,
        "F": 9,
        "F#": 10,
        "G": 11,
        "G#": 12,
    }
    return switcher.get(str(data.cell(row, column).value), 0)
def temp (maxElement):
    global database
    for i in range (0, len(database)):
        if database[i] == []:
            database[i].append(random.randint(0,maxElement - 1))
def setup(startDatabase, endDatabase, maxElement):
    global generation
    global genSize
    global data
    global database
    database = []
    generation = []
    Individual.bestChromosome = None
    Individual.bestFitness = 0
    for i in range (0, maxElement * maxElement):
        database.append([])
    #open the database file
    data = xlrd.open_workbook("Complex Final database.xlsx").sheet_by_index(0)
    createDatabase (startDatabase, endDatabase, maxElement)
    #DEBUG ONLY
    temp(maxElement)
    #print(database)
    #generation 0: all random lists of chromosomes
    for i in range (0, genSize):
        generation.append(Individual(randomChrom(maxElement), maxElement))
    #print(database)
def crossover(individuals):
    #input: list of two Individuals to cross
    global crossoverRate
    if random.random() > crossoverRate:
        return [individuals[0].getChromosome(), individuals[1].getChromosome()]
    length = len(individuals[0].getChromosome())
    splitpoint = random.randint(1, length - 2)
    return [individuals[0].getChromosome()[:splitpoint]+individuals[1].getChromosome()[splitpoint:],
            individuals[1].getChromosome()[:splitpoint]+individuals[0].getChromosome()[splitpoint:]]
def mutation(gen, maxElement):
    #input: generation list of individuals of size genSize
    global mutationRate
    #for each individual
    for ind in gen:
        #for each index in the chromosome
        newChrom = ind.getChromosome()
        for i in range(0, len(newChrom)):
            if random.random() < mutationRate:
                #mutate
                newChrom[i] = random.randint(0, maxElement - 1)
        ind.setChromosome(newChrom)
    return gen
def createNextGen(maxElement):
    global generation
    newGen = []
    for i in range(0, int(genSize / 2)):
        #choose random sample with sampleSize and mate top two
        sublist = random.sample(generation, sampleSize)
        bestFitness = [0, 0]
        bestIndividuals = [None, None]
        #get parents
        for ind in sublist:
            if ind.getFitness() > bestFitness[0] or ind.getFitness() > bestFitness[1]:
                #replace with one of these
                if bestFitness[0] > bestFitness[1]:
                    bestFitness[1] = ind.getFitness()
                    bestIndividuals[1] = ind
                else:
                    bestFitness[0] = ind.getFitness()
                    bestIndividuals[0] = ind
        #mate parents
        newChromosomes = crossover(bestIndividuals)
        #print(newChromosomes[0])
        newGen.append(Individual(newChromosomes[0], maxElement))
        newGen.append(Individual(newChromosomes[1], maxElement))
    newGen = mutation(newGen, maxElement)
    generation = newGen
def doGA(startDatabase, endDatabase, maxElement):
    #startDatabase- what column to start creating the database from
    #maxElement- max integer for each slot in the list
    global bestNotes
    global bestRhythms
    setup(startDatabase, endDatabase, maxElement)
    #print("Old")
    #print(Individual.bestFitness)
    #print(getCloseness())
    for i in range (0, iterations):
        createNextGen(maxElement)
    #print("New")
    #print(Individual.bestFitness)
    #print(getCloseness())
    if maxElement == 13:
        bestNotes = Individual.bestChromosome
    else:
        bestRhythms = Individual.bestChromosome
    #print(Individual.bestChromosome)
def most_common(lst):
    return max(set(lst), key=lst.count)
def getNew():
    global database
    newDatabase = []
    for i in database:
        if i == []:
            newDatabase.append(0)
        else:
            newDatabase.append(most_common(i))
    return newDatabase
def getCloseness():
    database1 = getNew()
    database2 = Individual.bestChromosome
    score = 0
    for i in range(0, len(database1)):
        if database1[i] == database2[i]:
            score += 1
    return score

#----------------PLAY BACK MUSIC--------------------#
def createMusic ():
    global bestNotes
    global bestRhythms
    songLength = 50
    #notes
    song = []
    song.append(random.randint(0, 12))
    song.append(random.randint(0, 12))
    for i in range(2, songLength):
        index = song[i-2] * 13 + song[i-1]
        #print("%d: %d, %d" % (index, song[i-2], song[i-1]))
        song.append(bestNotes[index])
    print("song")
    print(song)
    #rhythms
    rhythm = []
    rhythm.append(random.randint(0, 7))
    rhythm.append(random.randint(0, 7))
    for i in range(2, songLength):
        index = rhythm[i-2] * 8 + rhythm[i-1]
        rhythm.append(bestRhythms[index])
    print("rhythm")
    print(rhythm)
    playMusic(song, rhythm)
        
def playMusic(song, rhythm):
    pyglet.options['audio'] = ('openal', 'silent')
    switcherNotes = {
#pyglet.media.load("A.wav").play()
        1: "A.wav", #A
        2: "A#.wav",#A#
        3: "B.wav",#B"
        4: "C.wav",#C"
        5: "C#.wav",#C#"
        6: "D.wav",#D"
        7: "D#.wav",#D#"
        8: "E.wav",#E"
        9: "F.wav",#F"
        10: "F#.wav",#F#"
        11: "G.wav",#G"
        12: "G#.wav" #G#"
    }
    switcherRhythms = {
        0: 0.75,
        1: 0.0625,
        2: 0.125,
        3: 0.25,
        4: 1.5,
        5: 0.5,
        6: 3,
        7: 1
    }
    #player = pyglet.media.Player()
    for i in range(0, len(song)):
        totalTime = 0
        while(totalTime < switcherRhythms[rhythm[i]]):
            if song[i] != 0:
                pyglet.media.load(switcherNotes[song[i]], streaming=False).play()
            #time.sleep(switcherRhythms[rhythm[i]]*.5)
            time.sleep(.0625*1.5)
            totalTime += .0625
#pyglet.media.load("A.wav").play()
#notes
doGA(3, 33, 13)
#bestNotes = getNew()
#getNew()
#rhythms
doGA(4, 33, 8)
#bestRhythms = getNew()
#getNew()
#createMusic()

songs = [
[  7, 10, 5, 10, 9, 7, 8, 5, 8, 6, 11, 11, 0, 8, 6, 11, 11, 0, 8, 6],#: 300
[0, 3, 1, 1, 4, 1, 0, 1, 2, 3, 2, 6, 9, 7, 12, 9, 3, 0, 4, 3],#: 400
[9, 3, 4, 2, 10, 7, 8, 6, 8, 10, 6, 3, 3, 12, 3, 2, 3, 4, 2, 10],#: 500
[5, 12, 10, 9, 2, 7, 9, 5, 8, 6, 4, 3, 9, 10, 3, 4, 6, 9, 8, 6],#: 600
[6, 12, 4, 11, 4, 7, 5, 4, 10, 1, 6, 9, 4, 2, 11, 3, 2, 3, 11, 6],#: 700
[2, 2, 3, 8, 10, 11, 1, 0, 3, 9, 9, 8, 1, 8, 10, 11, 1, 0, 3, 9],#: 800
[5, 1, 1, 4, 6, 11, 0, 9, 1, 0, 11, 6, 6, 8, 2, 10, 6, 1, 1, 4],#: 900
[7, 2, 9, 6, 2, 9, 6, 2, 9, 6, 2, 9, 6, 2, 9, 6, 2, 9, 6, 2],#: 1000
[2, 0, 0, 9, 5, 12, 11, 10, 8, 2, 8, 0, 2, 10, 3, 5, 9, 7, 4, 4],#: 2000
[12, 6, 0, 10, 7, 10, 3, 5, 1, 8, 8, 1, 4, 2, 4, 11, 1, 3, 5, 1]#: 3000
]
rhythms = [
[3, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],#: 300
[2, 7, 3, 2, 2, 0, 1, 2, 2, 0, 1, 2, 2, 0, 1, 2, 2, 0, 1, 2],#: 400
[6, 4, 5, 5, 4, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],#: 500
[7, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],#: 600
[3, 5, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],#: 700
[1, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],#: 800
[2, 3, 1, 1, 4, 4, 5, 4, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],#: 900
[7, 2, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],#: 1000
[0, 2, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],#: 2000
[7, 2, 5, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]#: 3000
]
'''
song = []
for i in songs:
    for j in i:
        song.append(j)
rhythm = []
for i in rhythms:
    for j in i:
        rhythm.append(j)
playMusic(song, rhythm)'''

print("NOTES")
for i in range(0, len(songs)):
    switcherNote = {
        0:"rest",
        1:"A",
        2:"A#",
        3:"B",
        4:"C",
        5:"C#",
        6:"D",
        7:"D#",
        8:"E",
        9:"F",
        10:"F#",
        11:"G",
        12:"G#"
    }
    switcherRhythm = {
        0: "Dotted Eighth",
        1: "Sixteenth",
        2: "Eighth",
        3: "Quarter",
        4: "Dotted quarter",
        5: "Half",
        6: "Dotted half",
        7: "Whole"
    }
    notes = ""
    beats = ""
    for j in range(0, len(songs[i])):
        notes += switcherNote[(songs[i])[j]] + ", "
        beats += switcherRhythm[(rhythms[i])[j]] + ", "
    print("NNNNNNNNNNnext1")
    print(notes)
    print(beats)
