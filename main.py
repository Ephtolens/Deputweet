import requests
import pandas as pd
import os
from zipfile import ZipFile
from authlib.integrations.requests_client import OAuth1Auth
from time import sleep
from dateutil import parser

URL_VOTES_MD5 = "https://data.assemblee-nationale.fr/travaux-parlementaires/votes"
URL_STRUCTURE_MD5 = "https://data.assemblee-nationale.fr/acteurs/deputes-en-exercice"

URL_DOWNLOAD_VOTES = "http://data.assemblee-nationale.fr/static/openData/repository/15/loi/scrutins/Scrutins_XV.json.zip"
URL_DOWNLOAD_STRUCTURE = "http://data.assemblee-nationale.fr/static/openData/repository/15/amo/deputes_actifs_mandats_actifs_organes_divises/AMO40_deputes_actifs_mandats_actifs_organes_divises_XV.json.zip"

URL_RAPPORT_VOTE = "https://www2.assemblee-nationale.fr/scrutins/detail/(legislature)/15/(num)/{}"

TWITTER_API_URL = "https://api.twitter.com/2/tweets"

PATH_VOTES_MD5 = "votes/md5.txt"
PATH_STRUCTURE_MD5 = "structure/md5.txt"
PATH_VOTES_DONE = "votes/votes_done.txt"  

STORAGE_DIR_VOTES = "votes"
STORAGE_DIR_STRUCTURE = "structure"

PATH_TO_REPO_DIR = "/home/ephtolens/Deputweet"


MONTH = ['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

def retrieve_data(url, md5_file, url_dl, path_dir):
    with open(md5_file, 'r') as file:
        current_md5 = file.readline()

    r = requests.get(url)    
    new_md5 = r.text.split('MD5</h4>')[1].split("</p>")[0].split('<p>')[-1]

    if new_md5 != current_md5:
        download_and_unzip_file(url_dl, path_dir)
        
        with open(md5_file, 'w') as file:
            file.write(new_md5)


def download_and_unzip_file(url, extract_dir):
    local_filename = url.split('/')[-1]

    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        with open(f'{local_filename}', 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)

    with ZipFile(f'{local_filename}', 'r') as zip:
        zip.extractall(extract_dir)

    return local_filename



if __name__ == "__main__":
    print("here")
    # Change working directory
    os.chdir(PATH_TO_REPO_DIR)

    # Retrieve struture of AN : acteurs, organes, ...
    retrieve_data(URL_STRUCTURE_MD5, PATH_STRUCTURE_MD5,URL_DOWNLOAD_STRUCTURE,STORAGE_DIR_STRUCTURE)
    
    # Retrieve votes of AN
    retrieve_data(URL_VOTES_MD5,PATH_VOTES_MD5, URL_DOWNLOAD_VOTES,STORAGE_DIR_VOTES)

    # Load already tweeted votes
    with open(PATH_VOTES_DONE) as file:
        votes_done = []

        for l in file.readlines():
            votes_done.append(l[:-1])

    # Load credentials for bot accounts
    twitter_credentials = pd.read_csv('twitter_credentials.csv')

    votes = os.listdir(f"{STORAGE_DIR_VOTES}/json")
    for vote in votes:
        if vote not in votes_done:
            scrutin = pd.read_json(f"{STORAGE_DIR_VOTES}/json/{vote}")["scrutin"]
            numero = scrutin['numero']
            result = 'Adopté ✅' if scrutin['sort']['code']=='adopté' else 'Rejeté ❌'
            date = parser.parse(scrutin['dateScrutin'])
            ventiled_vote = pd.DataFrame(scrutin["ventilationVotes"]['organe']['groupes']['groupe'])
            pours = []
            contres = []
            non_votants = []
            abstentions = []
            for i in ventiled_vote['vote']:
                abss = i['decompteNominatif']['abstentions']
                if abss is not None:
                    abss = abss['votant']
                    if type(abss) == dict:
                        abss = [abss]

                    for a in abss:
                        abstentions.append(a['acteurRef'])


                nvs = i['decompteNominatif']['nonVotants']
                if nvs is not None:
                    nvs = nvs['votant']
                    if type(nvs) == dict:
                        nvs = [nvs]

                    for nv in nvs:
                        non_votants.append(nv['acteurRef'])

                ps = i['decompteNominatif']['pours']
                if ps is not None:
                    ps = ps['votant']
                    if type(ps) == dict:
                        ps = [ps]

                    for p in ps:
                        pours.append(p['acteurRef'])

                cs = i['decompteNominatif']['contres']
                if cs is not None:
                    cs = cs['votant']
                    if type(cs) == dict:
                        cs = [cs]

                    for c in cs:
                        contres.append(c['acteurRef'])
            
            htmllink = URL_RAPPORT_VOTE.format(numero)

            for index_account in range(len(twitter_credentials)):
                code_dep = twitter_credentials['code_dep'][index_account] 
                
                TWITTER_API_KEY = twitter_credentials['TWITTER_API_KEY'][index_account]
                TWITTER_API_KEY_SECRET = twitter_credentials['TWITTER_API_KEY_SECRET'][index_account]
                TWITTER_ACCESS_TOKEN = twitter_credentials['TWITTER_ACCESS_TOKEN'][index_account]
                TWITTER_ACCESS_TOKEN_SECRET = twitter_credentials['TWITTER_ACCESS_TOKEN_SECRET'][index_account]
                client = OAuth1Auth(client_id=TWITTER_API_KEY,client_secret= TWITTER_API_KEY_SECRET, token=TWITTER_ACCESS_TOKEN, token_secret=TWITTER_ACCESS_TOKEN_SECRET)

                if code_dep in pours:
                    vote_choice = "Pour"
                elif code_dep in contres:
                    vote_choice = "Contre"
                elif code_dep in non_votants:
                    vote_choice = "Non votant"
                elif code_dep in abstentions:
                    vote_choice = "Abstention"
                else:
                    vote_choice = "Non présent 💨"
                
                tweet = f"Scrutin n°{numero} du {date.day} {MONTH[date.month-1]} {date.year}\nVote: {vote_choice}\nStatut: {result}\nLien: {htmllink}"
                TWITTER_PARAM = {"text": tweet}
                twiter_post_tweet = requests.post(url= TWITTER_API_URL,json= TWITTER_PARAM, auth=client, headers={'Content-Type': 'application/json'})
                status_code = twiter_post_tweet.status_code
                if status_code != 201:
                    print(f'{code_dep}: Status_code {status_code}, Response {twiter_post_tweet.json()}')

            with open(PATH_VOTES_DONE, 'a') as file:
                file.write(vote + '\n')
                votes_done.append(vote)
