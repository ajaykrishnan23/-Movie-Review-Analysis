import requests, nltk
from bs4 import BeautifulSoup
from sentic import SenticPhrase
from nltk.corpus import stopwords

page = requests.get("https://www.imdb.com/showtimes/location?ref_=inth_ov_sh_sm")
soup = BeautifulSoup(page.content,'html.parser')
movie_content = soup.find_all("div",{"class" : "lister-item-image ribbonize"})
movie_links = []
for movie in movie_content:
    a_tag = (list(movie.children))[1]
    print()
    movie_links.append('https://www.imdb.com' + str(a_tag.get('href')))


movie_content = [] #links to title page of each movie
title = [] #movie names
for movie in movie_links:
    page = requests.get(movie)
    soup = BeautifulSoup(page.content,'html.parser')
    a_tag = list((soup.find('h4')).children)[0]
    movie_content.append('https://www.imdb.com' + str(a_tag.get('href')))
    title.append(str(a_tag.get('title')))


movie_links = [] #user reviews links
stars = []#stores the star ratings
for movie in movie_content:
    page = requests.get(movie)
    soup = BeautifulSoup(page.content,'html.parser')
    page = soup.find("div",{"class" : "user-comments"})
    star = soup.find("span",{"itemprop" : "ratingValue"}).get_text()
    stars.append(star)
    if str(type(page)) != '<class \'NoneType\'>':
        a_tag = (list(page.children))[len(list(page.children)) - 2]
        movie_links.append('https://www.imdb.com' + str(a_tag.get('href')))
    else:
        movie_links.append('No reviews yet')


polarity = [] #polarity of each and every movie
crew = [] #crew of each movie
for i in range(len(movie_links)):
    movie_content = []#stores the movie reviews
    pol = 0.00
    n = 0
    dict = {}
    crew1 = []
    if movie_links[i] != 'No reviews yet':
        page = requests.get(movie_links[i])
        soup = BeautifulSoup(page.content,'html.parser')
        page = soup.find_all("div",{ "class": "text show-more__control"})
        movie_content = [ review.get_text() for review in page]
        stop = stopwords.words('english')
        for singlereview in movie_content:
            names = []
            singlereview = ' '.join([i for i in singlereview.split() if i not in stop])
            sentences = nltk.sent_tokenize(singlereview)
            #sentences = sentences.lower()
            sentences = [nltk.word_tokenize(sent) for sent in sentences]
            sentences = [nltk.pos_tag(sent) for sent in sentences]
            for tagged_sentence in sentences:
                for chunk in nltk.ne_chunk(tagged_sentence):
                    if type(chunk) == nltk.tree.Tree:
                        if chunk.label() =='PERSON':
                            names.append(''.join([c[0] for c in chunk]))
            crew1.append(names)
        #finding the cast
        for name in crew1[0]:
            if name not in dict:
                dict[name] = 1
            else:
                dict[name] += 1
        for i in range(1,len(crew1)):
            for name in crew1[i]:
                if name not in dict:
                    dict[name] = 1
                else:
                    dict[name] += 1
        crew1 = []
        for key in dict:
            if dict[key]>=1:
                crew1.append(key)
        crew.append(crew1)

        for i in range(len(movie_content)):
            sp = SenticPhrase(movie_content[i])
            pol += sp.get_polarity()
            n += 1
        polarity.append(pol/n)
    else:
        polarity.append(0.00)
        crew.append([])
print(crew)
print("\n\n",len(crew),len(title))
print('\n\n\n\n\n\t\t\t\t\t\t\t\tMOVIE REVIEW')
for i in range(len(title)):
    print('Title:    ',title[i])
    print('Stars:    ',stars[i])
    print('Polarity: ',polarity[i])
    print('Crew:\n')
    for name in crew[i]:
        if len(crew[i]) != 0:
            print('\t'+name+'\n')
    print('\n')
