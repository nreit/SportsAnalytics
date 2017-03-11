import requests
from bs4 import BeautifulSoup, Comment
from lxml import html
import pandas as pd
import datetime as dt
import csv


#Function to get data ready for Pandas
def group(lst, n):
	for i in range(0, len(lst), n):
		val = lst[i:i+n]
		if len(val) == n:
			yield tuple(val)

#Empty lists to append data to
all_links = []
player_links = []

df = pd.DataFrame()

#df = pd.DataFrame(columns=['Player', 'Team', 'Date', 'Location', 'Opponent', 'Result', 'TimeOnIce', 'GoalsAgainst', 'ShotsAgainst', 'Saves', 'SavePercentage', 'PenaltiesInMinutes', 'ShootoutAttempts', 'ShootoutSaves'])

#Open the CSV file and write headers to it
fileCSV = open('goalieData.csv', 'wb')
headersForCSVFile = ['Player', 'Team', 'Date', 'Location', 'Opponent', 'Result', 'TimeOnIce', 'GoalsAgainst', 'ShotsAgainst', 'Saves', 'SavePercentage', 'PenaltiesInMinutes', 'ShootoutAttempts', 'ShootoutSaves']
writer = csv.writer(fileCSV)
writer.writerow(headersForCSVFile)


for number in range(1, 10):
	baseURL = "http://www.foxsports.com/nhl/players?teamId=0&season=2016&position=5&page="
	endURL = "&country=0&grouping=0&weightclass=0"
	url = baseURL + str(number) + endURL
	page = requests.get(url)
	tree = html.fromstring(page.content)
	for link in tree.xpath('//a/@href'):
		all_links.append(link)
	for each_link in all_links:
		if '-player' in each_link:
			player_links.append(each_link)
		else:
			pass

for player in player_links:
	playerPageBaseURL = "http://www.foxsports.com"
	playerPageEndURL = "-game-log"
	playerURL = playerPageBaseURL + str(player) + playerPageEndURL
	pagePlayer = requests.get(playerURL)


	tables = []
	messyStats = []
	stats = []

	#pagePlayer = requests.get("http://www.foxsports.com/nhl/jake-allen-player-game-log")

	try:
		soup = BeautifulSoup(pagePlayer.content, "html.parser")
		tables.append(soup.find_all(class_="wisfb_dataContainer"))
		for table in tables:
			for line in table:
				for num in line:
					messyStats.append(str(num))

		for item in messyStats:
			if ">" in item:
				split = item.split(">")
				info = split[1]
				stats.append(info[:-3])
			else:
				stats.append(item)

		stats = map(lambda s: s.strip(), stats)
		stats = filter(None, stats)

		popList = []

		for each in stats[1::12]:
			if each.isupper():
				baseIndexNumber = stats.index(each)
				goodDictionary = {'start': (int(baseIndexNumber - 13)), 'end': (int(baseIndexNumber - 2))}
				popList.append(goodDictionary)

		try:
			dictionaryIndexPop = popList[0]
			del stats[dictionaryIndexPop['start']:dictionaryIndexPop['end']]
		except:
			pass

		tree = html.fromstring(pagePlayer.content)
		firstName = tree.xpath('//*[@id="wisfb_nhlPlayerBio"]/div[2]/div[1]/div[2]/h1/text()')
		lastName = tree.xpath('//*[@id="wisfb_nhlPlayerBio"]/div[2]/div[1]/div[2]/h1/span/text()')
		name = ''.join([str(a) + b for a,b in zip(firstName,lastName)])
		team = tree.xpath('//*[@id="wisfb_nhlPlayerBio"]/div[2]/div[2]/span[1]/a/text()')
		team = ''.join(team)


		pandasReady = list(group(stats, 12))
		dfIndividual = pd.DataFrame(pandasReady, columns = ['Date', 'Location', 'Opponent', 'Result', 'TimeOnIce', 'GoalsAgainst', 'ShotsAgainst', 'Saves', 'SavePercentage', 'PenaltiesInMinutes', 'ShootoutAttempts', 'ShootoutSaves'])

		playerName = ([name] * len(dfIndividual))
		playerTeam = ([team] * len(dfIndividual))
		playerNameReady = pd.DataFrame(playerName)
		playerTeamReady = pd.DataFrame(playerTeam)

		dfIndividual.insert(0, 'Player', playerNameReady)
		dfIndividual.insert(1, 'Team', playerTeamReady)

		df = df.append(dfIndividual, ignore_index=True)
		
		print dfIndividual

	except:
		pass

# FOX SPORTS PAGES WITH LINKS TO ALL GOALIE PAGES
#http://www.foxsports.com/nhl/players?teamId=0&season=2016&position=5&page=1&country=0&grouping=0&weightclass=0
# FOX SPORT PAGE FOR EACH GOALIE STATS
# http://www.foxsports.com/nhl/jake-allen-player-game-log


'''
#Empty lists to throw raw data into
pandasReady = []

#for team in teamCodes:
	#BeautifulSoup request for the specific page
	#urlBase = "http://www.hockey-reference.com/players/"
	#urlEnd = "/gamelog/2017/"
	#print team
	#url = urlBase + team + urlEnd

url = "http://www.hockey-reference.com/players/l/lundqhe01/gamelog/2017/"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
#Empty List
rawTable = []
rawHTML = []
messyStats = []
stats = []

#Basic Statistics retrieval
tablesAll = soup.find_all("table")
for basic_stats in tablesAll:
	rawTable.append(basic_stats)
teamStatsTable = rawTable[0]
for html in teamStatsTable:
	rawHTML.append(html)
abTable = rawHTML[-1]
for block in abTable:
	for tdLine in block:
		for statNumber in tdLine:
			messyStats.append(str(statNumber))

for itemLine in messyStats:
	if ">" in itemLine:
		split = itemLine.split(">")
		info = split[1]
		stats.append(info[:-3])
	else:
		stats.append(itemLine)


pandasReady = list(group(stats, 15))
print pandasReady'''


#tree = html.fromstring(page.content)
#textTable = tree.xpath('//*[@id="gamelog"]/tbody/text()')
#print textTable
#pandasReady.append(tuple(teamStats))
						#print len(teamStats)
						#pandasReady = list(group(teamStats, 26))
						#df = pd.DataFrame(pandasReady)
#print pandasReady

#df = pd.DataFrame(pandasReady)
#date = ([str(dt.datetime.today().strftime("%m/%d/%Y"))] * len(df))
#print date
#dateReady = pd.DataFrame(date) 
#df.insert(1, 'DateAdded', dateReady)

df.to_csv(fileCSV, index=False, header = False, mode='a')

fileCSV.close()

