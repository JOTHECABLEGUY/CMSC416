## POS Tagger Scoring program ##
# Implemented by Jordan Dube for PA 3 for CMSC 416 w/ Prof. McInnes
# Credit to the slides and docs.python.org for providing insights into helpful features and tips #
# Python 3.9.12

# usage: python scorer.py prediction_file.txt true_file.txt
#			prediction_file.txt -> string filename of a file in the same folder as this program that was output by the tagger. 
#									These are the predictions that will be read and used to calculate accuracy against the correct set of tags
#			true_file.txt -> string filename of a file in the same folder as this program that will be read and used as the gold standard to evaluate the tagger predictions


# In addition to the problem specified in the tagger.py program problem statement, we want to evaluate the quality 
#		of the trained tagger based on the performance and accuracy of the tagger against a standard.
#		In this case, the standard is a manually tagged set of tokens (the same set on which the tagger ran predictions). 
#		This will allow us to test the efficacy of new rules that we introduce to the tagger. 

## Note: for the example run, a much shorter test file ('small-pos-test.txt') was used by the tagger for readability purposes, see tagger.py description for contents of this file. 
##			The original training file ('pos-train.txt') was used in tagging. Given these facts, a smaller true_file was used to correspond to the smaller prediction_file size as opposed to
##			a run of the program with the full pos-test.txt provided by Prof. McInnes. 
##			The contents of the 'small-pos-test-key.txt' (first 25 lines of 'pos-test.txt'): 

##												No/RB ,/, 
##												[ it/PRP ]
##												[ was/VBD n't/RB Black/NNP Monday/NNP ]
##												./. 
##												But/CC while/IN 
##												[ the/DT New/NNP York/NNP Stock/NNP Exchange/NNP ]
##												did/VBD n't/RB 
##												[ fall/VB ]
##												apart/RB 
##												[ Friday/NNP ]
##												as/IN 
##												[ the/DT Dow/NNP Jones/NNP Industrial/NNP Average/NNP ]
##												plunged/VBD 
##												[ 190.58/CD points/NNS ]
##												--/: most/JJS of/IN 
##												[ it/PRP ]
##												in/IN 
##												[ the/DT final/JJ hour/NN ]
##												--/: 
##												[ it/PRP ]
##												barely/RB managed/VBD to/TO stay/VB 
##												[ this/DT side/NN ]
##												of/IN 
##												[ chaos/NN ]
##												./.

## Example run (the output is piped into pos-test-with-tags.txt):
##		%python scorer.py pos-test-with-tags.txt small-pos-test-key.txt > pos-tagging-report.txt

##	Nothing printed to the console, but below are the contents of pos-tagging-report.txt:

##	 ACCURACY = 0.8541666666666666


##	 PREDICTED ->  NNP | ,  |PRP |VBD | RB | .  | IN | DT | NN | CD |NNS | :  |JJS | JJ |VBN | TO | VB 
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual RB   :  1  | 0  | 0  | 0  | 2  | 0  | 0  | 0  | 2  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual NNP  :  11 | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual CC   :  1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual ,    :  0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual PRP  :  0  | 0  | 3  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual VBD  :  0  | 0  | 0  | 3  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual .    :  0  | 0  | 0  | 0  | 0  | 2  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual IN   :  0  | 0  | 0  | 0  | 0  | 0  | 5  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual DT   :  0  | 0  | 0  | 0  | 0  | 0  | 0  | 4  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual VB   :  0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual NN   :  0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 2  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual CD   :  0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual NNS  :  0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual :    :  0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 2  | 0  | 0  | 0  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual JJS  :  0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual JJ   :  0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##	 actual TO   :  0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  
##	 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Description of scorer.py:

###		This program reads in the predictions output by the tagger.py program, eliminates any whitespace and converts everything to lowercase. 
###		The program then reads in the contents of the key file with the correctly tagged words. In this true file, all whitespace and phrasal boundary 
###		markers are replaced by a single space character (' ') and then split on the same character to get all tokens that will be used. For each of
###		these tokens, they can be further split into the word and the POS. We only take the POS because the tagger only outputs the tags. In the case 
###		of ambiguous tags, the first one is used. We then create a confusion matrix holder as well as a correct counter. From here we move onto the
###		actual scoring process, where each tag that was predicted is compared to the correct tag. If the tagger predicted correctly, increment the counter.
###		While this comparision is occurring, we update the confusion matrix with predicted-actual pairs of predicted tags to quantify the numbers of
###		confused tags and highlight areas for improvement. Once all tokens have been compared, calculate accuracy as the number of correct predictions 
###		divided by the total number of predictions. Print this accuracy to STDOUT. Then we create a Pandas DataFrame from the confusion matrix. 
###		Due to the lack of entries in the dictionary, we must replace all N/A values with 0, and then we cast to uint16 to store and access easier.
###		Print the columns to STDOUT using | as a separator to improve readability. For each row in the dataframe, we then print the index of the 
###		row (actual xyz) along with a formatted row with values separated by the | character. The values line up with the columns printed prior.
###		I went with a manual formatting approach because it gives more control to specify formatting.


#### 	Below are the accuracies output for each stage of rule creation. These values are derived from using scorer.py on the output from tagger.py on the whole
####	set of tokens in 'pos-test.txt' and 'pos-test-key.txt', not the shortened version I used to show the example run. Each stage is denoted by the set of rules I
####	used. For more detailed explanation of each stage, please refer to the description of tagger.py in which I explain the rationale behind different rules and
####	what the rules are. As we can see, accuracy increases with each rule addition (yet some rules may still not be optimal since I did not calculate the full picture 
####	of precision and recall).

#### BASELINE ACC: 	0.8313916654934534
####	rule 1:			0.8372870618048712
#### 	rule 1-2:		0.8627340560326623
####	rule 1-3:		0.8671160073208504
####	rule 1-4:		0.871251583837815
#### 	rule 1-5:		0.8721490919329861


# imports
from re import sub
from sys import argv, stdout
from pandas import DataFrame
from collections import defaultdict

# Scorer class to analyze the output from tagging and generate a confusion matrix
class Scorer():

	# constructor that takes a file with the tags generated from the 
	#		tagger.py program and a file with the correct tags to compare against
	def __init__(self, prediction_file, true_file):

		# open the file with the output tags and strip them
		with open(prediction_file, 'r') as f:
			self.predictions = list(map(str.strip, f.readlines()))
		# convert the predicted tags to lowercase
		self.predictions = list(map(str.lower, self.predictions))

		# open the file with the correct tags 
		with open(true_file, 'r') as f:
			self.actuals = f.read()

		# substitute all whitespace and phrasal boundaries with a single space 
		#	to allow split operation to capture all tokens properly
		self.actuals_presplit = sub(r'(\[|\]|\n|\s|\t)', ' ', self.actuals).split(' ')

		# get the actual tags from these tokens. In the event of ambiguous tags, grab the first one
		self.actuals = [t.rsplit('/', 1)[1].split('|')[0] for t in self.actuals_presplit if '/' in t]
		self.actuals = list(map(str.lower, self.actuals))

		# create a defaultdict to hold occurences or predicted-actual pairs (confusion matrix)
		self.confusion_matrix = defaultdict(lambda: defaultdict(int))

		# init counter to keep track of accurate predictions. float to enforce float division in accuracy calculation
		self.num_correct = 0.0

	# scoring function to alter the dataframe and 
	def score(self):

		# for each pairing of predicted tag to actual tag
		for (actual, predicted) in zip(self.actuals, self.predictions):

			# if they are the same, then a correct prediction was made, so increase the correct prediction counter
			if actual == predicted:
				self.num_correct += 1

			# update the value stored in the dataframe
			self.confusion_matrix[f'{predicted.upper()}'][f'actual {actual.upper()}'] += 1

		# calculate simple accuracy and print it to stdout
		print(f'ACCURACY = {self.num_correct/len(self.predictions)}\n\n')

		# take up space to align columns
		print(f'PREDICTED ->  ', end = '')

		# make a dataframe of the confusion matrix to make the printing process easier, fill unknown with 0, cast everything to uint16 to reduce memory
		confusion_df = DataFrame(self.confusion_matrix).fillna(0).astype('uint16')

		# justify along center of block (no more than 4 digits per cell so pad to 4 places) to print columns at top of table
		print('|'.join(list(map(lambda x: x.center(4), confusion_df.columns.to_list()))))
		print(f'{"-"*193}')

		# loop through the rows
		for index, row in confusion_df.iterrows():

			# convert row values to strings
			l = list(map(str, row.values))

			# justify the cell values along center to 4 places, use | to separate cells in the same row
			string = '|'.join(list(map(lambda x: x.center(4), l)))

			# justify the row name along the left to 12 places, then print the row values and print a line to separate the rows
			print(f'{index.ljust(12)}: {string}\n{"-"*193}')

	# method to run the scorer
	def run(self):
		self.score()

# obligatory ifmain to start the program 
if __name__ == '__main__':

	# args from the user
	args = argv[1:]

	# initialize Scorer with the 2 required files
	scorer = Scorer(args[0], args[1])

	# run the scorer
	scorer.run()
