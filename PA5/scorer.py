## Sentiment Analysis Scoring program ##
# Implemented by Jordan Dube for PA 5 for CMSC 416 w/ Prof. McInnes
# Credit to Prof. McInnes, the slides, and docs.python.org for providing insights into helpful features and tips #
# Python 3.9.12

# usage: python scorer.py prediction_file.txt true_file.txt
#			prediction_file.txt -> string filename of a file in the same folder as this program that was output by sentiment.py 
#									These are the predictions that will be read and used to calculate accuracy against the correct set of sentiments
#			true_file.txt -> string filename of a file in the same folder as this program that will be read and used as the gold standard to evaluate the predictions


# In addition to the problem specified in the sentiment.py program problem statement, we want to evaluate the quality 
#		of the trained model based on the performance and accuracy of the Sentiment Predictor model against a standard.
#		In this case, the standard is a manually assigned set of instances (the same set on which sentiment.py ran predictions). 
#		This will allow us to test the efficacy of the rules and features used by the model. 

## Example run:
##		%python scorer.py my-sentiment-answers.txt sentiment-test-key.txt
##
##		ACCURACY = 0.6982758620689655
##
##		PREDICTED ->        negative | positive
##		------------------------------------------
##		actual negative  :     42    |    30
##		------------------------------------------
##		actual positive  :     40    |   120
##		------------------------------------------

### Description of scorer.py:

###		This program reads in the predictions output by the sentiment.py program, and extracts the instance id and the sentiment predicted for each instance
###		passed into sentiment.py. The true file is then read and the same fields are extracted as seen from the predictions file.
###		We then create a confusion matrix holder as well as a correct counter. From here we move onto the actual scoring process, 
###		where each sentiment that was predicted is compared to the correct sentiment. The instance IDs must also be the same. 
###		If the model predicted correctly, increment the counter. While this comparision is occurring, we update the 
###		confusion matrix with predicted-actual pairs of predicted sentiments to quantify the numbers of confused sentiments and 
###		highlight areas for improvement. Once all sentiments have been compared, calculate accuracy as the number of correct predictions 
###		divided by the total number of predictions. Print this accuracy to STDOUT. Then we create a Pandas DataFrame from the confusion matrix. 
###		Due to a possible lack of entries in the dictionary, we must replace all N/A values with 0, and then we cast to uint16 to store and access easier.
###		Print the columns to STDOUT using | as a separator to improve readability. For each row in the dataframe, we then print the index of the 
###		row (actual sentiment x) along with a formatted row with values separated by the | character. The values line up with the columns printed prior.
###		I went with a manual formatting approach because it gives more control to specify formatting.

#### BASELINE ACC 		: 0.6896551724137931
####	with rule 1		: 0.7025862068965517
####	with rules 1-2	: 0.7198275862068966
####	with rules 1-3	: 0.6982758620689655

# imports
from re import search
from sys import argv
from pandas import DataFrame
from collections import defaultdict

# scorer class to score the predictions made by sentiment.py
class Scorer():

	# method to process the input files
	def proc_in_file(self, file):

		# open the file and read the lines
		with open(file, 'r') as f:
			contents = f.readlines()

		# format the lines into id-sentiment pairs to make comparison easier
		id_value_pairs = [search(r'answer instance="(.*)" sentiment="(.*)"', line).groups() for line in contents]

		# return the pairs
		return id_value_pairs

	# Scorer constructor that takes a prediction file name with the output from sentiment.py and a true file name with the correct sentiments
	def __init__(self, prediction_file, true_file):

		# process the input files
		self.predictions = self.proc_in_file(prediction_file)
		self.actuals = self.proc_in_file(true_file)

		# create a dictionary to store counts for predicted-actual pairs
		self.confusion_matrix = defaultdict(lambda: defaultdict(int))

	# score method to handle the logic and confusion matrix building
	def score(self):

		# keep track of number of correct predictions
		num_correct = 0.0

		# 1-1 compare the predictions to the correct answer, increment correct counter if the prediction was correct
		for (actual, predicted) in zip(self.actuals, self.predictions):
			if actual[0] == predicted[0] and actual[1] == predicted[1]:
				num_correct += 1

			# update the confusion matrix
			self.confusion_matrix[f'{predicted[1]}'][f'actual {actual[1]}'] += 1

		# print the accuracy
		print(f'ACCURACY = {num_correct/len(self.predictions)}\n')

		# print predicted to aid in formatting
		print(f'PREDICTED ->{" " * 7}', end = '')

		# convert the confusion matrix to a DataFrame
		confusion_df = DataFrame(self.confusion_matrix).fillna(0).astype('uint16')

		# print the column names along the top of the matrix (predicted)
		print('|'.join(list(map(lambda x: x.center(10), confusion_df.columns.to_list()))))
		print(f'{"-"*42}')

		# loop through the rows
		for index, row in confusion_df.iterrows():

			# convert the numbers to strings
			l = list(map(str, row.values))

			# format the values to fit into the table
			string = '|'.join(list(map(lambda x: x.center(10), l)))

			# print the row and a separator line
			print(f'{index.ljust(17)}: {string}\n{"-"*42}')

	# method to run the scoring method
	def run(self):
		self.score()

# main function to start the Scorer program
def main():

	# get the args from the command line
	args = argv[1:]

	# initialize a Scorer using the filenames from the command line
	scorer = Scorer(args[0], args[1])

	# run the program
	scorer.run()

# obligatory ifmain
if __name__ == '__main__':
	main()
