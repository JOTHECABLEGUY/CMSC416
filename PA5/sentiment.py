## Sentiment Predictor program ##
# Implemented by Jordan Dube for PA 5 for CMSC 416 w/ Prof. McInnes
# Credit to Prof. McInnes, the slides, and docs.python.org for providing insights into helpful features and tips #
# Python 3.9.12

# usage: python sentiment.py train_file.txt test_file.txt model_file.txt
#			train_file.txt -> string filename of a file in the same folder as this program that will be read and used to train the model that will predict on the test file
#			test_file.txt -> string filename of a file in the same folder as this program that will be read and predicted on by the trained the Sentiment Predictor model


# The problem is that we want to determine what the best sentiment is for messages sent on Twitter. If we are able to determine the most appropriate sentiment for a given tweet, then 
#	our language comprehension and analysis abilities expand greatly, and we can use these sentiments to extract information about the topic or situation addressed by the tweet. 
#	This helps us get an understanding of multiple opinions and a general "sentiment" surrounding the topic. Text sentiment analysis can help people in many fields to resolve
#	ambiguous meaning surrounding topics without manual annotation and can reduce the need for human intervention with machine text comprehension.

## Note: The nature of the input data results in large data points that are provided. The test and training instances are very similar with the only difference being 
##		the presence of a line giving the actual sentiment of the word. An example training instance is provided below:
##		<instance id="620821002390339585">
##		<answer instance="620821002390339585" sentiment="negative"/>
##		<context>
##		Does @macleansmag still believe that Ms. Angela Merkel is the "real leader of the free world"?  http://t.co/isQfoIcod0 (Greeks may disagree
##		</context>
##		</instance>

## Example run (only first 5 lines are shown, but one line is output for each test instance):
##		%python sentiment.py sentiment-train.txt sentiment-test.txt my-model.txt
##		<answer instance="620979391984566272" sentiment="negative"/>
##		<answer instance="621340584804888578" sentiment="positive"/>
##		<answer instance="621351052047028224" sentiment="positive"/>
##		<answer instance="621357165211742208" sentiment="negative"/>
##		<answer instance="621392677519540224" sentiment="positive"/>

### Description of sentiment.py:

###		This program reads in the text from both the given training and test files, uses regexes to extract the lexelt item,
###		the corpus language, the instance id, the context, and the sentiment assigned to the tweet if it is present. The context
###		of the tweet is processed by replacing some characters
###		(some punctuation and whitespace) with a single space. At this point we have all the unigrams
###		with a single space between them. We then split on whitespace to get a list of words.
###		Just in case any irregularities occurred, this list is filtered to remove any empty tokens. If a sentiment was given in the 
###		instance (meaning it was found in the training data), then the word-sentiment pair is used to increment 2 counters 
###		to make probability calculation easier. The extracted features are then put into a list as a representation
###		of an instance. This instance is then put into a list of similiar structures found in the file being processed.
###		Once all lines in the file have been used, the instances and both counter dictionaries are returned to the main
###		program. 

###		From here we open the model file that was given in the command line and write a header in it to help organize
###		the data that gets written to it later. We then initialize a few dictionaries to keep track of the probabilities 
###		of the sentiments given the words and the log-likelihood of the words as well as the occurrences of sentiments within the training 
###		data. The program then builds the most common sentiment dictionary to keep track of the occurrences of a sentiment within
###		the entire corpus to be used in the baseline case. From here we go on to building the probability dictionary which keeps 
###		track of the probability of a sentiment given a word, so it is more granular than the previous dictionary. The loop
###		also keeps track of which sentiment had the highest probability for a given word, which is crucial for the decision list
###		used later on. After this is done the probability dictionary is used to fill the log_likelihood dictionary using the 
###		probabilities of each sentiment for the word. The higher this value is, the more discriminative the word is, so it should be used
###		before other tests. The ratio can only be taken when there are 2 sentiments possible as seen in the training data,
###		so if there is only 1 possible sentiment, then the value stored is only the absolute value of the log of the probability
###		of the word given the 1 sentiment. From here the tests are built from the word, the sentiment more associated with the word, 
###		and the log-likelihood associated with the word. These 3 values are then used to create a list of tuples. This list 
###		is the test list. The tests are then put into descending order based on the 3rd value, the log-likelihood ratio which
###		was mentioned earlier to be a measure of discriminative power. The tests are then written to the model file for review
###		and the file is closed. From here we move into the testing and predicting phase. 

###		The baseline function is still present, but it is not used in this version. The baseline function simply gets 
###		the highest frequency of a sentiment and assigns that sentiment to the word. With the current training data, this 
###		results in every instance in the test data being predicted to have a positive sentiment since that is the 
###		most common sentiment. The decision list method is slightly more complex in that it runs the tests found in the 
###		init function in the most discriminative order so that as soon as a test passes, the sentiment is predicted and 
###		it moves to the next instance to test. The predictions are printed to STDOUT in the same format as can be 
###		found in the key file. The prediction file can then be passed into the scoring program per the guidelines 
###		found in scorer.py. In addition to the tests being conducted in the aforementioned order, there are 3 further features
###		being tested for. The first test is if there is the word 'not' in the context before the word that is found, the 
###		sentiment associated with the word is inverted as the prediction. The second test is if there is a monetary amount
###		(denoted by a '$' character followed by a number), then assign positive if the amount is less than 500 and negative if 
###		the amount is 500 or more. The third test looks for a mention ('@' followed by a string), and if the word 'help', 
###		'google', 'microsoft', or 'amazon' is found in the string, then the sentiment assigned if negative, and positive otherwise.

#### As taken from scorer.py:
####		ACCURACY = 0.6982758620689655
####
####		PREDICTED ->        negative | positive
####		------------------------------------------
####		actual negative  :     42    |    30
####		------------------------------------------
####		actual positive  :     40    |   120
####		------------------------------------------

#### The decision list was described above as the presence of the most discriminiative features are tested for in the
####		context of the instance. If the feature is present, then the test passes and the sentiment associated with that test
####		is assigned to the instance and a prediction is printed. 

# imports
from sys import argv, stderr
from re import search, sub
from collections import defaultdict
from numpy import log10, float32

# Sentiment Predictor class to handle predicting tweet sentiment
class Sentiment_Predictor():

	# method to process the input training and test files, file is a string of the file name to process
	def proc_in_file(self, file):

		# make a list to store the representations of each instance
		instances = []

		# dictionary to store counts for word -> correct sentiment pairs for the training set
		word_sentiment_dict = defaultdict(lambda: defaultdict(int))

		# dictionary to store counts for each possible word sentiment in the corpus
		sentiment_dict = defaultdict(int)

		# read in the file line by line
		with open(file, 'r') as f:
			contents = f.readlines()

		# the first 2 lines detail the corpus language and the lexelt item (ONLY PRESENT IN TRAINING FILE)
		corp_lang_s, lexelt_item_s = search(r'corpus lang="(.*)">', contents[0]), search(r'lexelt item="(.*)">', contents[1])
		
		# if the input file being processed is the training file, then use the groups to assign the corpus language and item
		if corp_lang_s and lexelt_item_s:
			
			corpus_lang = corp_lang_s.groups()[-1]
			lexelt_item = lexelt_item_s.groups()[-1]

			# start index is move forward 2 and end is reduced by 2
			start = 2
		
		# if not then manually assign the lang and item
		else:
			corpus_lang = 'en'
			lexelt_item = 'sentiment'

			# start index is 0
			start = 0

		# loop through the lines from the file. Start value depends on if corpus lang line was found
		for index in range(start, len(contents)-start):

			# check if the current line tells the instance id
			if (match := search(r'instance id="(.*)">', contents[index])):

				# store the id
				ID = match.groups()[-1]

				# increment index
				index += 1

				# check for the sentiment id for the current instance (from the instance id)
				if (match := search(fr'answer instance="{ID}" sentiment="(.*)"/>', contents[index])):

					# store the sentiment
					sentiment = match.groups()[-1]

				# if there is no answer line (testing set), sentiment is null
				else:
					sentiment = None

				# increment the index
				index += 1

				# Search for the context of the tweet
				if search(r'<context>', contents[index]):

					# if found, increment index to go to the line where the context actually starts
					index += 1

					# replace whitespace, some punctuation, and numbers with a single space. There is a pretty
					#	small chance of finding a specific number in the test set, and some punctuation should not impact
					#	discriminating between sentiment.
					context = sub(r'(\s+|\.|,|\')', ' ', contents[index]).lower()

					# split the context on whitespace and filter out empty tokens
					context = list(filter(lambda x: x, context.split(' ')))

					# if a sentiment was found (in the training set)
					if sentiment:

						# loop through the context
						for word in context:

							# increment word-sentiment pair count
							word_sentiment_dict[word][sentiment] += 1

							# increment sentiment count
							sentiment_dict[sentiment] += 1

					# increase index by 2 to skip the context close tag
					index += 2

				# if no context, it is null
				else:
					context = None

				# add the instance representation to the list
				instances.append([corpus_lang, lexelt_item, ID, context, sentiment])

		# return the instances found and the 2 counting dictionaries
		return instances, word_sentiment_dict, sentiment_dict

	# Model constructor, takes in 3 file names: a training file, a test file, and a file to store details of the model
	def __init__(self, train_file, test_file, model_file):

		# process the training file and the test file
		self.train_instances, self.train_word_sentiment_dict, train_sentiment_dict = self.proc_in_file(train_file)
		self.test_instances, _, _ = self.proc_in_file(test_file)

		# create a file handler within the class to write data to the model file
		self.model_file = open(model_file, 'w')

		# write a header into the model file with the feature name (word) and the log-likelihood/sentiment associated with it
		self.model_file.write('feature'.ljust(25) + ' log-likelihood'.ljust(15)+'  sentiment'.ljust(15)+'\n')
		self.model_file.write('-'*55+'\n')

		# create dictionaries to hold data: first to hold the probabilities of each word given the sentiment seen in the training data
		#									second to hold log likelihood values for each word
		#									third to hold the sentiment that each word maps to (the most frequent sentiment for the word)
		#									fourth to hold information about the most frequent sentiment for the entire corpus
		prob_word_dict = defaultdict(lambda: defaultdict(float32))
		log_likelihood_dict = defaultdict(float32)
		word_sentiment_max_dict = defaultdict(str)
		self.most_common_sentiment_dict = defaultdict(lambda: defaultdict(int))

		# loop through extracted instances and increase the counter for the sentiment
		for instance in self.train_instances:
			self.most_common_sentiment_dict[instance[1]][instance[4]] += 1

		# loop through the word->sentiment dictionary 
		for word, sentiments in self.train_word_sentiment_dict.items():

			# set a max count initialized to 0, the second element is null, but it will be the sentiment associated with the highest count
			max_count = (0, None)

			# loop through the counts stored in the table for the current word
			for sentiment, count in sentiments.items():

				# calculate the probability of the word given the sentiment count(sentiment|word)/count(sentiment)
				prob = count/train_sentiment_dict[sentiment]

				# store the probability in the table
				prob_word_dict[word][sentiment] = prob

				# if the count is higher than the max found, update the max_count value
				if count > max_count[0]:
					max_count = (count, sentiment)

			# once all possible sentiments of the word are processed, map the most frequent sentiment of the current word in the dictionary
			word_sentiment_max_dict[word] = max_count[1]

		# once the probabilities have been calculated, loop through the table
		for word, sentiments in prob_word_dict.items():

			# get a list of the word-sentiment pairs for the current word
			sentiment = list(sentiments.items())

			# if there are 2 possible sentiments, find the log ratio to determine discriminativity
			if len(sentiment) == 2:
				sentiment1, prob1 = sentiment[0]
				sentiment2, prob2 = sentiment[1]

				# store the value in the log table by the word
				log_likelihood_dict[word] = abs(log10(prob1/prob2))

			# else there is only one sentiment and the ratio is instead just the log of the probability of the current word
			else:
				log_likelihood_dict[word] = abs(log10(prob1))

		# create tests to run with the word, the sentiment associated with the word, and the log likelihood associated with the word
		self.tests = [(word, word_sentiment_max_dict[word], log_likelihood_dict[word]) for word in list(self.train_word_sentiment_dict.keys())]
		
		# sort (rank) the tests according to discriminatory power
		self.tests.sort(key = lambda item: item[2], reverse = True)

		# output the test statistics to the model file
		for test in self.tests:
			self.model_file.write(f'{test[0].ljust(25)} {str(round(test[2], 5)).ljust(15)} {test[1].ljust(15)}\n')

		# close the model file
		self.model_file.close()

	# method to get the baseline predictions, which is just predicting the most common sentiment seen in the training instances
	def baseline(self):

		# loop through the testing instances
		for instance in self.test_instances:

			# get a list of the possible sentiments the word can be
			options = list(self.most_common_sentiment_dict[instance[1]].items())

			# sort the options by raw frequency
			options.sort(key = lambda item: item[1], reverse = True)

			# output the guess in the proper format
			print(f'<answer instance="{instance[2]}" sentiment="{options[0][0]}"/>')

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

					# TEST 1: if 'not' is found before the current word, then invert the sentiment that comes with the word being tested
					if context.index(word) > 1 and 'not' in context[:context.index(word)]:
						sentiment = 'negative' if test[1] == 'positive' else 'positive'

					# if it isnt found, then the sentiment that comes with the test is used (no inversion)
					else:
						sentiment = test[1]
					print(f'<answer instance="{instance[2]}" sentiment="{sentiment}"/>')
					break

				# TEST 2: get any money amounts, if the amount is less than 500, then assign positive, else negative
				elif (match := search(r'\$(\d+)', word)):
					if int(match.groups()[-1]) < 500:
						sentiment = 'positive'
					else:
						sentiment = 'negative'
					print(f'<answer instance="{instance[2]}" sentiment="{sentiment}"/>')
					break

				# # TEST 3: check every word in the context, if an instance of @x is found, then check for the words help, google, microsoft, amazon
				# #		if these words are found, then assign negative, else positive
				else:

					# need a flag to stop when an instance is found
					s = 0
					for w in instance[3]:
						if (match := search(r'@(\w+)\b', w)):
							if search(r'(help|google|microsoft|amazon)', match.groups()[-1]):
								sentiment = 'negative'
							else:
								sentiment = 'positive'
							s = 1
							print(f'<answer instance="{instance[2]}" sentiment="{sentiment}"/>')
							break
					if s:
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

	# create a Sentiment Predictor object with the proper file names from the command line
	s_p = Sentiment_Predictor(train_file, test_file, model_file)

	# run the prediction program
	s_p.run()

# obligatory ifmain
if __name__ == '__main__':
	main()
