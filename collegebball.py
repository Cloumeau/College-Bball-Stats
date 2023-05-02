from bs4 import BeautifulSoup
import requests


def get_player_stats(url):
    # get the webpage content
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find all <a> tags that have "data-player-uids" in them and don't contain certain words
    players = []
    for a in soup.find_all('a', {'data-player-uid': True}):
        if not any(word in a.text for word in ['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks']):
            players.append(a.text.strip())

    # get the headers from the table
    table = soup.find('table', {'class': 'Table Table--align-right'})
    headers = table.findAll('th')

    # get the stats from the table
    rows = table.findAll('tr')
    data = []
    for row in rows[:-1]: # exclude last row
        cols = row.findAll('td')
        stats = []
        for col in cols:
            stats.append(col.text.strip())
        if len(stats) > 0:
            data.append(stats)

    # map the player names to the correct rows
    player_names = []
    for player in players:
        if player.strip() != '':
            player_names.append(player.strip())

    stats_with_names = []
    for i, stats in enumerate(data):
        # make sure we have a player name for this row
        if i < len(player_names):
            stats_with_name = {"Player": player_names[i]}
            for j in range(len(headers)):
                header_text = headers[j].text.strip()
                stat_text = stats[j].strip()
                stats_with_name[header_text] = stat_text
            stats_with_names.append(stats_with_name)

    # return the stats with names
    return stats_with_names

def get_team_mappings():
    url = 'https://www.espn.com/mens-college-basketball/teams'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    mappings = {}
    for link in soup.find_all('a', {'class': 'AnchorLink'}):
        href = link['href']
        if '/mens-college-basketball/team/_/id/' in href:
            team_id = href.split('/id/')[1]
            team_name = link.text
            mappings[team_id] = team_name

    return mappings

def get_team_id(team_mappings):
    team_name = input("Which team's stats do you want to see? ").lower()
    matching_teams = []
    for team_id, name in team_mappings.items():
        if team_name in name.lower():
            matching_teams.append(name)
    
    if len(matching_teams) == 0:
        print("No teams found with that search term.")
        return None
    elif len(matching_teams) == 1:
        return next(iter([k.split('/')[0] for k, v in team_mappings.items() if v == matching_teams[0]]))
    else:
        print("The search provided yielded multiple results, please select the intended team:")
        for i, team in enumerate(matching_teams):
            print(f"{i+1}.) {team}")
        selected_team_num = input("Enter the number of the intended team: ")
        while not selected_team_num.isnumeric() or int(selected_team_num) <= 0 or int(selected_team_num) > len(matching_teams):
            print("Invalid input. Please enter a valid team number.")
            selected_team_num = input("Enter the number of the intended team: ")
        return next(iter([k.split('/')[0] for k, v in team_mappings.items() if v == matching_teams[int(selected_team_num)-1]]))


def build_team_url(team_id):
    base_url = 'https://www.espn.com/mens-college-basketball/team/stats/_/id/'
    team = base_url + str(team_id)
    return team


#Villanova URL
# https://www.espn.com/mens-college-basketball/team/stats/_/id/222/season/2024




team_mappings = get_team_mappings()
team_id = get_team_id(team_mappings)
team_url = build_team_url(team_id)
stats = get_player_stats(team_url)
for stat in stats:
    print(stat)
