from django.shortcuts import render
import pandas as pd
import nltk
nltk.download('punkt')
from difflib import SequenceMatcher
import requests
from bs4 import BeautifulSoup as bs
import warnings

def plaigiarism(request):
    if request.method == 'POST':
        qry = request.POST['check']
        warnings.filterwarnings("ignore", module='bs4')

        stop_words = set(nltk.corpus.stopwords.words('english')) 
        def purifyText(string): 
            words = nltk.word_tokenize(string)
            return (" ".join([word for word in words if word not in stop_words]))

        def webVerify(string, results_per_sentence):
            sentences = nltk.sent_tokenize(string)
            matching_sites = []
            for url in searchBing(query=string, num=results_per_sentence):
                matching_sites.append(url)
            for sentence in sentences:
                for url in searchBing(query = sentence, num = results_per_sentence):
                    matching_sites.append(url)

            return (list(set(matching_sites)))
        def similarity(str1, str2):
            return (SequenceMatcher(None,str1,str2).ratio())*100

        def report(text):
            matching_sites = webVerify(purifyText(text), 2)
            matches = {}
            for i in range(len(matching_sites)):
                matches[matching_sites[i]] = similarity(text, extractText(matching_sites[i]))
            matches = {k: v for k, v in sorted(matches.items(), key=lambda item: item[1], reverse=True)}
            return matches

        def returnTable(dictionary):
            df = pd.DataFrame({'Similarity (%)': dictionary})
            return df

        def searchBing(query, num):
            url = 'https://www.bing.com/search?q=' + query
            urls = []
            page = requests.get(url, headers = {'User-agent': 'John Doe'})
            soup = bs(page.text, 'html.parser')
            for link in soup.find_all('a'):
                url = str(link.get('href'))
                if url.startswith('http'):
                    if not url.startswith('http://go.m') and not url.startswith('https://go.m'):
                        urls.append(url)
            
            return urls[:num]

        def extractText(url):
            page = requests.get(url)
            soup = bs(page.text, 'html.parser')
            return soup.get_text()
        def result(qry):
            return (returnTable(report(str(qry))))
        dt=result(qry)
        dk=dt.to_dict()
        newd=dk['Similarity (%)']
        return render(request,'plaigiarism.html',{'newd':newd})
    return render(request,'plaigiarism.html')
