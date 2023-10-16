## WSD program ##
# Implemented by Jordan Dube for PA 4 for CMSC 416 w/ Prof. McInnes
# Credit to Prof. McInnes, the slides, and docs.python.org for providing insights into helpful features and tips #
# Python 3.9.12

# usage: python wsd.py train_file.txt test_file.txt model_file.txt
#			train_file.txt -> string filename of a file in the same folder as this program that will be read and used to train the model that will predict on the test file
#			test_file.txt -> string filename of a file in the same folder as this program that will be read and predicted on by the trained WSD model


# The problem is that we want to determine what the best sense is for some word in text. If we are able to determine the most appropriate sense for a given word, then 
#	our language comprehension and analysis abilities expand greatly, and we can use these senses to extract information about the individual word that is assigned 
#	as well as information about the word's neighbors. Word Sense can greatly aid the growth of sentiment analysis. This field can help people in many fields to resolve
#	ambiguity surrounding usage of words with mulitple meanings and can even reduce the need for human intervention with machine text comprehension.

## Note: The nature of the input data results in large data points that are provided. The test and training instances are very similar with the only difference being 
##		the presence of a line giving the actual senseid of the word. An example training instance is provided below:
##		<instance id="line-n.w9_10:6830:">
##		<answer instance="line-n.w9_10:6830:" senseid="phone"/>
##		<context>
##		 <s> The New York plan froze basic rates, offered no protection to Nynex against an economic downturn that sharply cut demand and didn't offer flexible pricing. </s> <@> <s> In contrast, the California economy is booming, with 4.5% access <head>line</head> growth in the past year. </s> 
##		</context>
##		</instance>

## Example run (only first 5 lines are shown, but one line is output for each test instance):
##		%python wsd.py line-train.txt line-test.txt my-model.txt
##		<answer instance="line-n.w8_059:8174:" senseid="phone"/>
##		<answer instance="line-n.w7_098:12684:" senseid="phone"/>
##		<answer instance="line-n.w8_106:13309:" senseid="phone"/>
##		<answer instance="line-n.w9_40:10187:" senseid="phone"/>
##		<answer instance="line-n.w9_16:217:" senseid="phone"/>

### Description of tagger.py:

###		This program reads in the text from both the given training and test files, uses regexes to extract the lexelt item,
###		the corpus language, the instance id, the context, and the sense assigned to the word if it is present. The context
###		of the word is processed by removing the <head> tags from around the word being disambiguated after which some elements
###		(punctuation, numbers, whitespace) are replaced by a single space At this point we have all the unigrams
###		with a single space between them. We then split on whitespace to get a list of words.
###		Just in case any irregularities occurred, this list is filtered to remove any empty tokens. If a sense was given in the 
###		instance (meaning it was found in tthe training data), then the word-sense pair is used to increment 2 counters 
###		to make probability calculation easier. The extracted features are then put into a list as a representation
###		of an instance. This instance is then put into a list of similiar structures found in the file being processed.
###		Once all lines in the file have been used, the instances and both counter dictionaries are returned to the main
###		program. 

###		From here we open the model file that was given in the command line and write a header in it to help organize
###		the data that gets written to it later. We then initialize a few dictionaries to keep track of the probabilities 
###		of the senses given the words and the log-likelihood of the words as well as the occurrences of senses within the training 
###		data. The program then builds the most common sense dictionary to keep track of the occurrences of a sense within
###		the entire corpus to be used in the baseline case. From here we go on to building the probability dictionary which keeps 
###		track of the probability of a sense given a word, so it is more granular than the previous dictionary. The loop
###		also keeps track of which sense had the highest probability for a given word, which is crucial for the decision list
###		used later on. After this is done the probability dictionary is used to fill the log_likelihood dictionary using the 
###		probabilities of each sense for the word. The higher this value is, the more discriminative the word is, so it should be used
###		before other tests. The ratio can only be taken when there are 2 senses possible as seen in the training data,
###		so if there is only 1 possible sense, then the value stored is only the absolute value of the log of the probability
###		of the word given the 1 sense. From here the tests are built from the word, the sense more associated with the word, 
###		and the log-likelihood associated with the word. These 3 values are then used to create a list of tuples. This list 
###		is the test list. The tests are then put into descending order based on the 3rd value, the log-likelihood ratio which
###		was mentioned earlier to be a measure of discriminative power. The tests are then written to the model file for review
###		and the file is closed. From here we move into the testing and predicting phase. 

###		The baseline function is still present, but it is not used in this version. The baseline function simply gets 
###		the highest frequency of a sense and assigns that sense to the word. With the current training data, this 
###		results in every instance in the test data being predicted to have the sense of 'product' since that is the 
###		most common sense. The decision list method is slightly more complex in that it runs the tests found in the 
###		init function in the most discriminative order so that as soon as a test passes, the sense is predicted and 
###		it moves to the next instance to test. The predictions are printed to STDOUT in the same format as can be 
###		found in the key file. The prediction file can then be passed into the scoring program per the guidelines 
###		found in scorer.py

#### AS TAKEN FROM scorer.py:
##			ACCURACY = 0.8412698412698413

##			PREDICTED ->         phone   | product
##			------------------------------------------
##			actual phone     :     58    |    14
##			------------------------------------------
##			actual product   :     6     |    48
##			------------------------------------------

## The decision list was described above as the presence of the most discriminiative features are tested for in the
##		context of the instance. If the feature is present, then the test passes and the sense associated with that test
##		is assigned to the instance and a prediction is printed. 


# imports
from sys import argv
from re import search, sub
from collections import defaultdict
from numpy import log10, float32

# wsd class to handle predicting word sense
class WSD():

	# method to process the input training and test files, file is a string of the file name to process
	def proc_in_file(self, file):

		# make a list to store the representations of each instance
		instances = []

		# dictionary to store counts for word -> correct sense pairs for the training set
		word_sense_dict = defaultdict(lambda: defaultdict(int))

		# dictionary to store counts for each possible word sense in the corpus
		sense_dict = defaultdict(int)

		# read in the file line by line
		with open(file, 'r') as f:
			contents = f.readlines()

		# the first 2 lines detail the corpus language and the lexelt item
		corpus_lang = search(r'corpus lang="(.*)">', contents[0]).groups()[-1]
		lexelt_item = search(r'lexelt item="(.*)">', contents[1]).groups()[-1]

		# loop through the lines from the file. the first 2 have already been read and the last 2 lines are close tags
		for index in range(2, len(contents)-2):

			# check if the current line tells the instance id
			if (match := search(r'instance id="(.*)">', contents[index])):

				# store the id
				ID = match.groups()[-1]

				# increment index
				index += 1

				# check for the sense id for the current instance (from the instance id)
				if (match := search(fr'answer instance="{ID}" senseid="(.*)"/>', contents[index])):

					# store the sense
					sense = match.groups()[-1]

					# increment the index
					index += 1

				# if there is no answer line (testing set), sense is null
				else:
					sense = None

				# Search for the context of the word
				if search(r'<context>', contents[index]):

					# if found, increment index to go to the line where the context actually starts
					index += 1

					# replace the line word with a standard "line"
					context = sub(r'<head>(L|l)ine(s|-n|d)?</head>', 'line', contents[index])

					# replace whitespace, some punctuation, and numbers with a single space. There is a pretty
					#	small chance of finding a specific number in the test set, and most punctuation should not impact
					#	discriminating between senses.
					context = sub(r'(\s+|\.|,|\d+|\')', ' ', context)

					# split the context on whitespace and filter out empty tokens
					context = list(filter(lambda x: x, context.split(' ')))

					# if a sense was found (in the training set)
					if sense:

						# loop through the context
						for word in context:

							# increment word-sense pair count
							word_sense_dict[word][sense] += 1

							# increment sense count
							sense_dict[sense] += 1

					# increase index by 2 to skip the context close tag
					index += 2

				# if no context, it is null
				else:
					context = None

				# add the instance representation to the list
				instances.append([corpus_lang, lexelt_item, ID, context, sense])

		# return the instances found and the 2 counting dictionaries
		return instances, word_sense_dict, sense_dict

	# wsd constructor, takes in 3 file names: a training file, a test file, and a file to store details of the model
	def __init__(self, train_file, test_file, model_file):

		# process the training file and the test file
		self.train_instances, self.train_word_sense_dict, train_sense_dict = self.proc_in_file(train_file)
		self.test_instances, _, _ = self.proc_in_file(test_file)

		# create a file handler within the class to write data to the model file
		self.model_file = open(model_file, 'w')

		# write a header into the model file with the feature name (word) and the log-likelihood/sense associated with it
		self.model_file.write('feature'.ljust(25) + ' log-likelihood'.ljust(15)+'  sense'.ljust(15)+'\n')
		self.model_file.write('-'*55+'\n')

		# create dictionaries to hold data: first to hold the probabilities of each word given the sense seen in the training data
		#									second to hold log likelihood values for each word
		#									third to hold the sense that each word maps to (the most frequent sense for the word)
		#									fourth to hold information about the most frequent sense for the entire corpus
		prob_word_dict = defaultdict(lambda: defaultdict(float32))
		log_likelihood_dict = defaultdict(float32)
		word_sense_max_dict = defaultdict(str)
		self.most_common_sense_dict = defaultdict(lambda: defaultdict(int))

		# loop through extracted instances and increase the counter for the sense 
		for instance in self.train_instances:
			self.most_common_sense_dict[instance[1]][instance[4]] += 1

		# loop through the word->sense dictionary 
		for word, sense in self.train_word_sense_dict.items():

			# set a max count initialized to 0, the second element is null, but it will be the sense associated with the highest count
			max_count = (0, None)

			# loop through the counts stored in the table for the current word
			for sense, count in sense.items():

				# calculate the probability of the word given the sense count(sense|word)/count(sense)
				prob = count/train_sense_dict[sense]

				# store the probability in the table
				prob_word_dict[word][sense] = prob

				# if the count is higher than the max found, update the max_count value
				if count > max_count[0]:
					max_count = (count, sense)

			# once all possible senses of the word are processed, map the most frequent sense of the current word in the dictionary
			word_sense_max_dict[word] = max_count[1]

		# once the probabilities have been calculated, loop through the table
		for word, senses in prob_word_dict.items():

			# get a list of the word-sense pairs for the current word
			sense = list(senses.items())

			# if there are 2 possible senses, find the log ratio to determine discriminativity
			if len(sense) == 2:
				sense1, prob1 = sense[0]
				sense2, prob2 = sense[1]

				# store the value in the log table by the word
				log_likelihood_dict[word] = abs(log10(prob1/prob2))

			# else there is only one sense and the ratio is instead just the log of the probability of the current word
			else:
				log_likelihood_dict[word] = abs(log10(prob1))

		# create tests to run with the word, the sense associated with the word, and the log likelihood associated with the word
		self.tests = [(word, word_sense_max_dict[word], log_likelihood_dict[word]) for word in list(self.train_word_sense_dict.keys())]
		
		# sort (rank) the tests according to discriminatory power
		self.tests.sort(key = lambda item: item[2], reverse = True)

		# output the test statistics to the model file
		for test in self.tests:
			self.model_file.write(f'{test[0].ljust(25)} {str(round(test[2], 5)).ljust(15)} {test[1].ljust(15)}\n')

		# close the model file
		self.model_file.close()

	# method to get the baseline predictions, which is just predicting the most common sense seen in the training instances
	def baseline(self):

		# loop through the testing instances
		for instance in self.test_instances:

			# get a list of the possible senses the word can be
			options = list(self.most_common_sense_dict[instance[1]].items())

			# sort the options by raw frequency
			options.sort(key = lambda item: item[1], reverse = True)

			# output the guess in the proper format
			print(f'<answer instance="{instance[2]}" senseid="{options[0][0]}"/>')

	# method to run the predictions using the ranked tests
	def run_with_rules(self):

		# loop through instances extracted from the testing file
		for instance in self.test_instances:

			# run each test on the current instance
			for test in self.tests:
				word = test[0]
				context = instance[3]

				# if the word is found in the instance's context, print the prediction in the proper format and go to the next word
				if word in context:
					sense = test[1]
					print(f'<answer instance="{instance[2]}" senseid="{sense}"/>')
					break

	# method to run the prediction program
	def run(self):
		# self.baseline()
		self.run_with_rules()
		
# main function to start the program
def main():

	# get the args from the command line
	args = argv[1:]
	train_file = args[0]
	test_file = args[1]
	model_file = args[2]

	# create a WSD object with the proper file names from the command line
	wsd = WSD(train_file, test_file, model_file)

	# run the prediction program
	wsd.run()

# obligatory ifmain
if __name__ == '__main__':
	main()
