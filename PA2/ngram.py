## Ngram Extractor program ##
# Implemented by Jordan Dube for PA 2 for CMSC 416 w/ Prof. McInnes
# Credit to the slides, Prof. McInnes, and docs.python.org for providing insights into helpful features and tips #
# Python 3.9.12

# usage: python ngram.py n m file1.txt [file2.txt file3.txt ...]
# 			n -> integer denoting the desired number of tokens per ngram (higher value will result in sentences that are more similar to source material)
#			m -> integer denoting the desired number of sentences to generate
#			file1.txt -> string filename of a file in the same folder as this program that will be read and used to generate sentences
#			[file2.txt file3.txt ...] -> any number of additional files following the same restrictions as file1.txt

# The problem is that we want to extract meaning from natural language. Ngrams are used to aid in 
#		many applications of natural langauge processing, such as clustering (associating words based on number of
#		occurrences), multiword phrases based on association measures, and sentence generation. For this
#		assignment, the focus was sentence generation.

## Note: for the example run, a much shorter file was used to generate sentences for readability purposes.
##			The contents of 'small_ngram_input.txt' are: i love food. do you?
## Example run:
##		%python ngram.py 2 4 small_ngram_input.txt
##		This program generates random sentences based on an Ngram model.
##		This program was developed by Jordan Dube
##		Help and guidance received from these sources: class slides, Prof. McInnes, and docs.python.org
##
##		Command line settings : ngram.py 2 4
##		do you
##		i love food
##		i love food
##		i love food

### Description of ngram.py:
### 	This program reads text from text files (as many as the user provides), converts the text to lower case,
###		replaces punctuation with start and end tags, adds a start tag to the beginning, splits the contents on white space,
###		and eliminates other unnecessary characters. For unigram sentence generation, only the unigrams are used to find
###		the frequency of each unique token, and a random number is used to decide which token is used (more frequent tokens have
###		a higher chance of being chosen). For higher dimension models (bi+), 2 tables are needed, a table storing the counts
###		of each n-1 gram (e.g for a trigram model, each group of 2 words is stored along with its number of occurrences in the corpus)
###		and a table storing each word that can occur after each n-1 gram (e.g for a trigram model, this table will store the 2 words
###		the come before each word as well as the word. The combination of these "keys" is then counted). These tables are then
###		used to create a relative frequency table, which is used, similarly to the unigram model, to create thresholds that determine
### 	the next word in the sentence based on a randomly generated number. For all models (uni+), this process is repeated 
###		until an end tag is chosen, at which point the sentence is done and is printed to the terminal. 
###		This sentence generation repeats for a user-specified number of times 

# imports
from random import uniform
from sys import argv, exit
from re import sub
from collections import defaultdict
from bisect import bisect_left

# Ngram_Extractor class to process text files and generate sentences
class Ngram_Extractor:

	# constructor with args n (number of tokens per ngram), m (number of sentences to generate),
	# and files (list of txt files to read)
	def __init__(self, n = 1, m = 1, files = []):

		self.num_ngrams = n if n > 0 else 1 	# n cannot be 0 or below
		self.num_sentences = m 					# rename for clarity
		self.corpus = ''						# intializa corpus to merge contents of files 
		
		# for each file, lower case contents get added to corpus
		# 	white space is added to separate multiple files
		for file in files:
			with open(file, 'r') as f:
				self.corpus += f.read().lower()
				self.corpus += ' '
		
		# sub_dict contains undesired elements (mostly punctuation)
		#	and the corresponding "corrections". "'" is eliminated to avoid the 
		# 	problems that can arise from contractions
		sub_dict = {r'\.': f' <end> {" <start>"*(self.num_ngrams-1)} ',
					'!'  : f' <end> {" <start>"*(self.num_ngrams-1)} ', 
					r'\?': f' <end> {" <start>"*(self.num_ngrams-1)} ',
					','  : '',
					"'"  : '',
					'\n' : ' '}

		# use the sub dict to update the corpus
		for element, substitution in sub_dict.items():
			self.corpus = sub(element, substitution, self.corpus)
	
	# this method handles the tokenization of the text
	def extract(self):
		
		# filter out empty tokens, split by white space, and add n-1 start tokens to the beginning of the token list
		self.tokens = list(filter(lambda x: x, ['<start>']*(self.num_ngrams-1) + self.corpus.split(' ')))
		
		# delete any start tags from the end of the list (from punctuation substitution)
		while self.tokens[-1] == '<start>':
			del self.tokens[-1]
		
		# add an end tag to the end of the list if there isn't one already
		if self.tokens[-1] != '<end>':
			self.tokens.append('<end>') 

	# this method handles the building of both history and possible word tables (w and w-1 tables from slides)
	def build_w_w1_tables(self):

		# initialize dictionaries: ndict stores the ngrams and their counts (history, word)
		# 							hdict stores the beginning parts of ngrams and counts (history)
		self.ndict = defaultdict(lambda: defaultdict(int))
		self.hdict = defaultdict(int)

		# range objects to improve readability. words range stops at the point where the last word 
		#		is the last element in an ngram
		words_range = range(len(self.tokens)-self.num_ngrams+1)
		ngram_range = range(self.num_ngrams)

		# loop through each word
		for word_index in words_range:
			ngram = ['']*self.num_ngrams				# preallocate memory for each ngram being built (faster than building new lists with append)
			
			# loop through each index of the ngram
			for i in ngram_range:
				ngram[i] = self.tokens[word_index + i] 	# add words iteratively to form ngrams

				# if the last element of the ngram is not empty
				if ngram[-1]:
					w = ngram[-1] 						# the word to be stored is the last seen
					history = ' '.join(ngram[:-1]) 		# the history of the word is everything before the word
					
					# increase the counts in the n and h dicts
					self.ndict[history][w] += 1
					self.hdict[history] += 1
				elif '<end>' in ngram:
					break

	# This method builds the relative frequency table for bigram models and above
	def build_rel_freq_table(self):

		# calculate the relative frequency table (calculation ahead of time is faster)
		self.rel_freq_table = defaultdict(lambda: defaultdict(float))

		# loop through the recently created histories and words
		for hist_key, hist_value in self.hdict.items():
			for word_key, word_value in self.ndict[hist_key].items():

				# probability of a word given its history is the frequency of the word with its 
				#	history (ndict value) divided by the frequency of the history (hdict value)
				self.rel_freq_table[word_key][hist_key] = word_value/hist_value
	
	# This method builds the simple frequency table to be used by the unigram model. 
	# 	If history is not needed, then a simple frequency of number of occurrences / number of tokens
	#	is sufficient to weight the next word decision
	def build_unigram_frequency_table(self):
		
		unique_tokens = set(self.tokens) 				# get the unique tokens to make unigram dict
		num_tokens = float(len(self.tokens)) 			# get length of token list
		
		# match each unique token to frequency in the token list
		self.unigram_frequency_dict = {word:(self.tokens.count(word)/num_tokens) for word in unique_tokens}

	# method for choosing the next word based on the history (string) present
	def choose(self, history = None):

		# fetch a random number between 0 and 1 to be used as a point on imaginary "number line"
		num = uniform(0,1)
		
		# if the history is blank, then then unigram model is being used so return a word from the available choices
		if not history:
			poss_words = list(self.unigram_frequency_dict.keys())
			no_hist_rel_freqs = list(self.unigram_frequency_dict.values())
			thresholds = [sum(no_hist_rel_freqs[:i]) for i in range(len(no_hist_rel_freqs))]
			selected_word = poss_words[bisect_left(thresholds, num) - 1]
			return [selected_word]

		# list of possible words that the next word can be chosen from
		poss_words = list(self.ndict[history].keys())

		# calculate the relative frequencies for all possible choices of next word based on given history 
		#		using the relative frequency table
		poss_words_relative_frequencies = [self.rel_freq_table[word][history] for word in poss_words]
		
		# create array of probabilistic thresholds to decide on next word using the random number
		#	the thresholds are summations of the previous points on the number line
		thresholds = [sum(poss_words_relative_frequencies[:i]) for i in range(len(poss_words_relative_frequencies))] 
		
		# use builtin bisect library to find index of appropriate bin (returns index to right of bin, so subtract 1)
		selected_word = poss_words[bisect_left(thresholds, num) - 1]
		return [selected_word] 								# return the chosen next word
	
	# method to generate sentences using models greater than unigram (anything with history dependent decisions)
	def generate_sentence_multi(self):
		
		ngram_split_index = -self.num_ngrams + 1 			# index of beginning of ngram window (save on computation by declaring here)
		sentence = ['<start>']*(self.num_ngrams) 			# first part of sentence will have n start tags
		key = ' '.join(sentence[ngram_split_index:]) 		# put ngram in format of history
		curr_word = self.choose(key) 						# send history to choose method to get the next word

		# repeat until an end tag is returned
		while '<end>' not in curr_word:
			sentence.extend(curr_word) 						# add the new word to the sentence
			key = ' '.join(sentence[ngram_split_index:]) 	# slide ngram window down 1 index
			curr_word = self.choose(key) 					# get new word

		print(' '.join(sentence[self.num_ngrams:])) 		# when loop is broken, print out resulting sentence
	
	# method to generate a sentence when history is not needed (unigram model)
	def generate_sentence_base(self):
		sentence = [] 										# dont need any start tags, but does need initialization
		curr_word = []										# dont need to get new word from the start
		
		# while an end tag is not returned
		while '<end>' not in curr_word:
			sentence.extend(curr_word)						# add new word to the list
			curr_word = self.choose() 						# get new word using an empty history
		
		print(' '.join(sentence[1:]))						# print resulting sentence wen end tag reached
	
	# method to generate multiple sentences
	def generate_sentences(self):

		# the number of tokens per ngram -1 
		#	(the -1 is to make unigram model have a 0 for this variable)
		#	this value determines which branch taken by the program (whether to build history tables)
		n = self.num_ngrams-1
		
		# if n is above 0 this will be True (reason for subtracting 1 -> makes boolean logic easier)
		if n:
			self.build_w_w1_tables()				# build tables for history (w-1) and the word choices (w)
			self.build_rel_freq_table()				# build table with relative frequencies to help choose the next word
			
			# create desired number of sentences using the history-dependent method
			for _ in range(self.num_sentences):
				self.generate_sentence_multi()
		else:
			self.build_unigram_frequency_table()	# build table of simple frequencies since history is not used in the unigram model
			
			# create desired number of sentences using the history-independent method
			for _ in range(self.num_sentences):
				self.generate_sentence_base()
	
	# method to run the extraction and generation program
	def run(self):
		self.extract()								# process text
		self.generate_sentences()					# use information from extraction to generate sentences

# main method
def main():
	
	# check args to verify proper formatting, if not enough args, exit
	if len(argv) > 3:
		n, m = int(argv[1]), int(argv[2])		# convert the numbers to integers
		files = list(argv[3:]) 					# store the filenames in a list
	
	else:
		print('wrong usage')
		exit()

	# print opening line that details author, sources, and short description of the program
	print('This program generates random sentences based on an Ngram model.\n'+
			'This program was developed by Jordan Dube\n'+
			'Help and guidance received from these sources: class slides, Prof. McInnes, and docs.python.org\n\n'+
			f'Command line settings : {" ".join(argv[:3])}')
	
	extractor = Ngram_Extractor(n, m, files) 	# call extractor constructor with the command line arguments
	extractor.run() 							# run the program within the extractor class

# obligatory ifmain
if __name__ == '__main__':
	main()
