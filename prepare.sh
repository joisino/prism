wget https://mattr1.github.io/mctest/data/MCTestAnswers.zip
unzip MCTestAnswers.zip

wget https://nlp.stanford.edu/data/glove.6B.zip
unzip glove.6B.zip -d glove

gdown https://drive.google.com/uc?id=1DGSKxP4qH4Nmwbk9hiJ1ZdXZMl2CP2D9
unzip cand_words_French.zip

gdown https://drive.google.com/uc?id=10P0IEup90aQdDauOuGpwhDxeDzWp3492
unzip cand_words_German.zip

python download_nltk.py

