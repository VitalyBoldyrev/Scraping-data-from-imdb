The goal of this project - collect, process, analyse and present data from imdb.com. 

The idea is simple. I introduce a special measure of distance between actors. How is it measured? If two actors played in the same movie, the distance between them is 1. If two actors never played in the same move, but there is some actor, who played in some movies with each of the actors, then the distance between the actors is 2. And so on. Let's call it movie distance.
So, I obtained  all pairwise move distances for highest-paid actors of 2019. They are:


Dwayne Johnson
Chris Hemsworth
Robert Downey Jr.
Akshay Kumar
Jackie Chan
Bradley Cooper
Adam Sandler
Scarlett Johansson
Sofia Vergara
Chris Evans

I explored not all the movies, where an actor played, but only 5 latest movies. And only those actors, who played top 5 roles. 
More over,  that if a connection between two actors is bigger than 3, then there is no connection between the actors (infinite distance).

Then I visualed connections with NetworkX library and created a word cloud based on an actor's movies descriptions.
