## POS Tagger program ##
# Implemented by Jordan Dube for PA 3 for CMSC 416 w/ Prof. McInnes
# Credit to the slides and docs.python.org for providing insights into helpful features and tips #
# Python 3.9.12

# usage: python tagger.py train_file.txt test_file.txt
#			train_file.txt -> string filename of a file in the same folder as this program that will be read and used to train the tagger that will tag the test file
#			test_file.txt -> string filename of a file in the same folder as this program that will be read and tagged by the trained tagger


# The problem is that we want to determine what the best tag is for each word in text. If we are able to determine the most appropriate POS tag for a given word, then 
#	our language comprehension and analysis abilities expand greatly, and we can use these tags to extract information about the individual word that is tagged 
#	as well as information about the word's neighbors. As explored in the POS tagging paper, different domains often require a tagger to be trained using different sources. 
# 	The goal of this program is to solve the problem of POS tagging using the domain of the training file and the test file. 

## Note: for the example run, a much shorter test file ('small-pos-test.txt') was used by the tagger for readability purposes. The original training file ('pos-train.txt') was used. 
##			The contents of 'small-pos-test.txt' (first 25 lines of pos-test.txt): 

##												No , 
##												[ it ]
##												[ was n't Black Monday ]
##												. 
##												But while 
##												[ the New York Stock Exchange ]
##												did n't 
##												[ fall ]
##												apart 
##												[ Friday ]
##												as 
##												[ the Dow Jones Industrial Average ]
##												plunged 
##												[ 190.58 points ]
##												-- most of 
##												[ it ]
##												in 
##												[ the final hour ]
##												-- 
##												[ it ]
##												barely managed to stay 
##												[ this side ]
##												of 
##												[ chaos ]
##												.  

## Example run (the output is piped into pos-test-with-tags.txt):
##		%python tagger.py pos-train.txt small-pos-test.txt > pos-test-with-tags.txt

##	Nothing printed to the console, but below are the contents of pos-test-with-tags.txt:

##												nnp
##												,
##												prp
##												vbd
##												rb
##												nnp
##												nnp
##												.
##												nnp
##												in
##												dt
##												nnp
##												nnp
##												nnp
##												nnp
##												vbd
##												rb
##												nn
##												nn
##												nnp
##												in
##												dt
##												nnp
##												nnp
##												nnp
##												nnp
##												vbd
##												cd
##												nns
##												:
##												jjs
##												in
##												prp
##												in
##												dt
##												jj
##												nn
##												:
##												prp
##												nn
##												vbn
##												to
##												vb
##												dt
##												nn
##												in
##												nns
##												.

### Description of tagger.py:
###		This program reads in the text from both the given training and test files, converts everything to lowercase,
###		replaces all extra characters (whitespace and phrasal boundary markers) with a single space. At this point we have all the 
###		actual tokens with a single space between them. We then split on whitespace to get a list of tokens.
###		Just in case any irregularities occurred, this list is filtered to remove any empty tokens. The program loops through 
###		the training tokens, splits the token into the word and the POS, and increments a counter of the word-pos pair to track
###		occurrences. From here we go on to calculating the appropriate tag for each of the training tokens. First, we read in the test file again
###		without converting to lowercase and create an array to hold all the assigned tags up to the current word. For each token, 
###		there are five rules that are checked. From the table of word-pos pairs, we get the possible POS options and sort the options
###		based on the occurrences, so the first element of the list of options will be the tag with the highest probability given the word.
###		If the word did not appear in the training file, then it will not have any options, so it is assigned a tag of NN.
###		This most probable option (or NN) will be the selected tag, but it can be changed if it matches the rules. 

###		RULES SECTION OF DESCRIPTION:
###		These rules only apply if there was 0 or more than one possible option as determined by the occurrence table. This is because if there 
###		is only one possible tag for the word based on the training file, then it should not be changed. If there were 0 options,
###		then it was assigned NN, but it should be checked in case it can be changed based on rules. The first rule checked is 
###		if there is a spelled out word or \d ([0-9]) in the token, which will change the tag to CD (a number). The second rule to be checked is
###		if there is a capitalized letter in the original set of tags (without any case changes). If there is, then it is assigned to NNP (proper
###		noun). This rule sometimes changes the first word in a sentence to this tag, but it still increases the accuracy compared to omiting 
###		the rule. The third rule is if the predicted tag is a noun or number or jj, assign it NNS if it ends in "s". This was designed 
###		to catch plural nouns. The JJ and CD conditions were added after examining the amount of tokens predicted to be CD and JJ, but were in
###		fact NNS. The fourth rule is if the preceding word is predicted to be TO or MD, then assign VB if VB is in the list of available
###		options for the current word's POS. The fifth rule is if the word ends in "ing", then assign it VBG. This rule was designed to
###		catch gerunds. It may catch words such as ring or sing, but this rule does increase the accuracy compared to omiting it. 
###		Once the rules ar checked, the choice the tagger predicted is printed to STDOUT and the array of assigned tags is updated with
###		the most recent choice. The accuracies for a tagging of 'pos-test.txt' after being run through scorer.py can be found in the scorer.py description. 

# imports
from re import sub, search
from sys import argv
from collections import defaultdict

# Tagger class to take in a training file and use it to tag a test file
class Tagger():

	# function to process the input files. if the contents of the file should be converted to lowercase, set lower_toggle to 1
	def process_input_file(self, file, lower_toggle = 0):

		# open the file and read its contents. Convert to lowercase depending on the value of the toggle 
		with open(file, 'r') as f:
			contents = f.read().lower() if lower_toggle else f.read()

		# eliminate extraneous characters such as whitespace and phrasal boundaries and split on spaces
		substituted_contents = sub(r'(\[|\]|\n|\t|\s)', ' ', contents).split(' ')

		# only keep the tokens that are not empty
		filtered_contents = list(filter(lambda x: x, substituted_contents))

		# return the processed tokens
		return filtered_contents

	def __init__(self, train_file, test_file):

		# dictionary to store the counts of each token-tag pairing in the training set
		self.mapped = defaultdict(lambda: defaultdict(int))

		# process the input training and test token sets
		self.training_tokens = self.process_input_file(train_file, 1)
		self.test_tokens = self.process_input_file(test_file, 1)

		# make a variable to store the test file for use in the run_with_rules method
		self.test_file = test_file

		# loop through the training set because each token has 2 components
		for t in self.training_tokens:

			# split the token on the last / character
			s = t.rsplit('/', 1)

			# the word that is tagged is the first element in the list
			w = s[0]

			# the POS is the second component of the list, eliminate any ambiguity and take the first option
			pos = s[1].split('|')[0]

			# increase the number of occurences of the word-tag pair
			self.mapped[w][pos] += 1

	# function to get the baseline tag predictions
	def baseline(self):

		# loop through the tokens to be tagged
		for t in self.test_tokens:

			# the possible POS assignments are found in the defaultdict 
			options = list(self.mapped[t].items())

			# sort the options by the number of occurrences, the most frequent option will be the first element in the list
			options.sort(key = lambda item: item[1], reverse = True)

			# pick the most likely POS, if there are no options, then options is empty and we assume it is NN
			choice = options[0][0] if options else 'nn'

			# print the choice to stdout to be piped into the user-given file
			print(choice)

	# function to find the predicted tags given 5 additional rules
	def run_with_rules(self):

		# get a list of tokens from the original testing files to preserve capitalization
		self.original_test_tokens = self.process_input_file(self.test_file)

		# preallocate an array of empty strings to store the previous n assigned tags
		choices = [' '] * len(self.test_tokens)

		# loop through the tokens to be tagged
		for (i, t) in enumerate(self.test_tokens, start = 0):

			# the possible POS assignments are found in the defaultdict 
			options = list(self.mapped[t].items())

			# sort the options by the number of occurrences, the most frequent option will be the first element in the list
			options.sort(key = lambda item: item[1], reverse = True)

			# pick the most likely POS, if there are no options, then options is empty and we assume it is NN
			choice = options[0][0] if options else 'nn'

			## RULES ##
			# if there is only 1 option, then no further checking is needed because it was covered by the training text
			if len(options) != 1:

				## RULE 1: look for spelled out numbers and any digits in the token
				if search(r'(one|two|three|four|five|six|seven|eight|nin|\d+|thousand)', t):
					choice = 'cd'

				## RULE 2: look for capitalization in the original text, if there is a capital letter, most likely it is a proper noun
				elif search(r'[A-Z]', self.original_test_tokens[i]):
					choice = 'nnp'

				## RULE 3: if there is a noun or number or jj, assign it to a nns if it ends in "s"
				if choice in ['cd', 'nn', 'nnp', 'jj'] and search(r'\w+s$', t):
					choice = 'nns'

				## RULE 4: if the preceding word is assigned a to or md, then assign vb if it is an appropriate option
				if i >= 1 and (choices[i-1] in ['to','md'] and 'vb' in [o[0] for o in options if options]):
					choice = 'vb'

				## RULE 5: if a word ends in "ing", assign verb with a g (gerund?)
				if search(r'(\Bing\b)', t):
					choice = 'vbg'

			# print the choice to stdout to be piped into the user-given file
			print(choice)

			# update the choices array to be used in later tokens
			choices[i] = choice

	# function to run the tagger with the appropriate ruleset
	def run(self):
		# self.baseline()
		self.run_with_rules()

# ifmain
if __name__ == '__main__':

	# get list of files to feed into the tagger
	args = argv[1:]

	# initialize the tagger with the 2 files required
	tag = Tagger(args[0], args[1])

	# run the tagging program
	tag.run()