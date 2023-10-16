## Question-Answer System program ##
# Implemented by Jordan Dube for PA 6 for CMSC 416 w/ Prof. McInnes
# Credit to Prof. McInnes, the slides, and wikipedia.readthedocs.io/en/latest/code.html#api for providing insights into helpful features and tips #
# Python 3.9.12

# usage: python qa-system.py log_file.txt
#			log_file.txt -> string filename of a file to store information as the program progresses for review after the program terminates

# The problem is that we want to create a system capable of answering any question that a user can ask (as long as it is a "who", "what", "when", or "where" question).
#	Rather than use a pre-trained model, we want dynamic information retrieval through the use of the internet. With this system,
#	users would be able to access information quicker than they could on their own since they would be aided by a CPU's computational power.

## Example run:
##		%python python qa-system.py log_file.txt
##		*** This is a QA system by Jordan Dube.
##		        It will try to answer questions that start with Who, What, When or Where.
##		        Enter 'exit' to leave the program.
##		=?>     Who is George Washington
##		=>      George Washington is a 39-volume set edited by John Clement Fitzpatrick, whom the George Washington Bicentennial Commission commissioned.
##		=?>     Who was George Washington
##		=>      George Washington was an American military officer, statesman, and Founding Father who served as the first president of the United States from 1789 to 1797.
##		=?>     What is the Moon
##		=>      The Moon is Earth's only natural satellite.
##		=?>     What is an apple
##		=>      An apple is an edible fruit produced by an apple tree (Malus domestica.
##		=?>     When was Barack Obama born
##		=>      Barack Obama was born on August 4, 1961.
##		=?>     When did Edison die
##		=>      Edison died on October 18, 1931.
##		=?>     When is Christmas
##		=>      Christmas is on December 25.
##		=?>     Where is the Louvre
##		=>      The Louvre is in Paris, France.
##		=?>     Where is Virginia
##		=>      Virginia is in the Mid-Atlantic and Southeastern regions of the United States between the Atlantic Coast and the Appalachian Mountains.
##		=?>     exit
##		Thank you! Have a nice day! :)

## Below is an excerpt from the log file for the last search: "Where is Virginia"
##		=?>	Where is Virginia

##		SEARCHED FOR: Virginia is in
##		TITLES OF PAGES RETURNED: ['Virginia', 'West Virginia', 'Virginia is for Lovers', 'Virginia Beach, Virginia', 'Virgínia', 'Yes, Virginia, there is a Santa Claus', 'Richmond, Virginia', 'List of cities and counties in Virginia', 'Virginia Woolf', 'Arlington County, Virginia']

##		SENTENCE FOUND: Virginia, officially the Commonwealth of Virginia, is a state in the Mid-Atlantic and Southeastern regions of the United States between the Atlantic Coast and the Appalachian Mountains
##		USING PATTERN:re.compile('\\bVirginia\\b.*?\\bis\\b.*?\\bin\\b(.*)\\b,?')
##		ANSWER:  the Mid-Atlantic and Southeastern regions of the United States between the Atlantic Coast and the Appalachian Mountains
##		=>	Virginia is in the Mid-Atlantic and Southeastern regions of the United States between the Atlantic Coast and the Appalachian Mountains.
##		=?>	exit

### Description of qa-system.py:

###		This program starts by creating a QA object using the log file from the command line. It opens the file for writing into as well as compiles
###		some regexes that can be used later. Once this setup is done the program can not be run. The program prompts the user for an input question
###		that is of the who/what/when/where form. The question is then processed. the question mark is removed, 
###		the question is split into words, the verb to be is looked for, and an initial topic of the query is extracted.
###		Then, the program branches depending on what interrogative word was used. If it is a who question, the return type is set to 'person',
###		and if the verb to be was not found, the verb is changed to 'was' and the auxiliary words get assigned the last word in the query
### 	concatenated with 'by'. The program also indicates that the answer may come before the verb through the looking_back flag.
###		If it is a "when" question, the return type is set to date and the second word in the question is checked. If the second word
###		is 'did', then the last word is treated as the verb and it is converted to past tense with the addition of the word 'on'. 
###		If the last word in the query is not capitalized and the second word is 'was', then the last word in the question
###		is treated as the verb and the additional word 'on' is appended. If the last word is capitalized, then only the word 'on'
###		is needed. If it is a what question, no additional words are necessary and the return type is set to object. If it is a 
###		where question then the return type is 'place' and a check is done if the second word in the question is 'did' and if it is,
###		then the last word in the question is treated as the verb. In either case, the additional word 'in' is added to encourage
###		a lean towards location in the event of ambiguity. Once these steps have been taken, the question processing concludes with
###		extraction and storage or articles and a vector with the topic, looking back flag, articles, verbs, return type, and 
###		additional words are returned.

###		Once the question is processed, if there was an invalid format, then a message is sent to the user, otherwise the program
###		moves to getting the answer using the question. The individual components are then unpacked and used for building the query
###		that will be used to create a search query and the patterns to look for in the documents. If the looking back flag is set,
###		then 2 patterns are created, 1 to look for the answer before the topic and the other looks for the answer after the topic. 
###		If the flag isn't set then only 1 pattern is created to look after the topic. The patterns are then compiled, the search
###		is used to retrieve the top 10 ranked documents based on the query from Wikipedia. These 10 titles are then used to retrieve
###		their referenced pages. If any titles are ambiguous, then that term is not used, but the other titles are still checked.
###		There are multiple checks throughout the extraction process that check if an answer has been found, so as soon as an answer 
###		is extracted it can be returned. The contents of the pages are split by '.' into sentences, any sentence that matches a pattern
###		being checked is returned for further extraction. For every search and match event a new entry in the log file is generated.
###		If the initial extraction is unsuccessful, the return type is appended to the search query to further disambiguate the search.
###		If the results have been checked, and no match has been found, them the query is shortened by 1 word and the process repeats 
###		starting from building the search query. If no match is found with any query, then the program will answer that it cannot 
###		answer the question. If the return type is a date, the program conducts a series of tests that result in a standardized date
###		being extracted from the answer. If a match was found for a date return type, but there are no numbers in it, then it will
###		also register as unable to be answered. The answer is then condensed into a complete sentence using the topic, article, auxiliary
###		words, and the verb 'to be' if is was found/assign in question processing. This sentence is returned where it is logged and
###		printed to the user, after which they can ask their next question. This loop repeats until the user types 'exit'.

# imports
import wikipedia as w
import sys
import os
import re

# question-answering class
class QA():

	# init constructor, takes the name of a log file
	def __init__(self, log_file):

		# remove the file if it exists, we want to start fresh each run
		if os.path.exists(log_file):
			os.remove(log_file)

		# create a file handler for the log file, using append mode, but write mode would be the same
		self.log_file = open(log_file, 'a+', encoding='utf-8')

		# precompile a regex to check for upper case letters
		self.cap_check = re.compile(r'[A-Z]')
		
		# precompile a regex to check for numbers
		self.num_check = re.compile(r'\d')
		
		# precompile a regex to check for month names/abbreviations
		self.month_check = re.compile(r'\b([Jj]an|[Jj]anuary|[Ff]eb|[Ff]ebruary|[Mm]ar|[Mm]arch|[Aa]pr|[Aa]pril|[Mm]ay|[Jj]un|[Jj]une|[Jj]ul|[Jj]uly|[Aa]ug|[Aa]ugust|[Ss]ep|[Ss]eptember|[Oo]ct|[Oo]ctober|[Nn]ov|[Nn]ovember|[Dd]ec|[Dd]ecember)\b')
		
		# precompile a regex to check for the verb "to be" in user queries
		self.tobe_check = re.compile(r'(were|was|are|is)')

	# method to handle initial processing, outputs a vector to aid in answering the query
	def process_question(self, question):

		# remove the question mark if present
		question = question.rstrip('?')

		# split on whitespace
		q_split = question.split(' ')

		# interrogative word (who, what, when, where) will be at the beginning of the question
		q_word = q_split[0].lower()

		# find the verb to be
		q_verb = [word for word in q_split if self.tobe_check.match(word)]

		# if a match was found, then the q_word is the first occurrence in the list
		if q_verb:
			q_verb = q_verb[0]
		else:
			q_verb = ''

		# list of articles
		art_list = ['the', 'a', 'an']

		# placeholder for any auxiliary words to be included with the pattern to search for in documents
		aux_word = ''

		# flag to determine whether the answer can be found before the verb
		looking_back = False

		# topic of the sentence, basically everything except the verb
		topic = q_split[q_split.index(q_verb)+1:] if q_verb else q_split[2:]

		# check what the first word was to determine auxiliary words and return type
		# if a "who" question was asked (ex Who assassinated Abraham Lincoln?)
		if q_word == 'who':

			# we are looking for a person
			return_type = 'person'

			# if the verb "to be" was not found earlier
			if not q_verb:

				# the verb will be assigned 'was'
				q_verb = 'was'

				# assign auxiliary words of the second word in the sentence (most likely a verb, but it isnt "to be") 
				#		with the word "by" to enforce looking for the person who did the verb (ex Lincoln was assassinated by Booth)
				aux_word = f'{q_split[1]} by'

				# the answer may come before the verb (ex Booth assassinated Lincoln)
				looking_back = True

		# if a "when" question was asked (ex When did Thomas Jefferson die?)
		elif q_word == 'when':

			# if the second word is "did" (ex When did Edison die?)
			if q_split[1] == 'did' :

				# main verb most likely occurs at the end, change the verb tense to 
				#	past tense (VERY NAÏVE) and add "on" to better capture time information
				aux_word = f'{q_split[-1].rstrip("e")}ed on'

				# remove the last word of the question from the topic
				topic.remove(q_split[-1])

			# if the last word is not a proper noun and the second word in the question is "was"
			#	(ex When was George Washington born?)
			elif not self.cap_check.search(topic[-1]) and q_verb == 'was':

				# aux word is now the last word with "on" to enforce date
				aux_word = f'{q_split[-1]} on'

				# remove the verb from the topic
				topic.remove(q_split[-1])

			# If the last word is a proper noun, it cannot be a verb (ex When is Christmas)
			elif self.cap_check.search(topic[-1]):

				# still need "on" for dates
				aux_word = 'on'

			# we are looking for a date
			return_type = 'date'

		# if a "what" question is asked (ex What is the Moon)
		elif q_word == 'what':

			# what is very general, so we are simply looking for an object; no aux words really apply here
			return_type = 'object'

		# if a "where" question is asked (ex Where is the Louvre)
		elif q_word == 'where':

			# we always need "in"
			aux_word = 'in'

			# if the second word is "did" (ex Where did Iron Man premier?)
			if q_split[1] == 'did' :

				# try to convert last word (verb) to past tense, add the preposition "in"
				aux_word = f'{q_split[-1].rstrip("e")}ed in'

				# remove the likely verb from the topic
				topic.remove(q_split[-1])

			# we are looking for a place
			return_type = 'place'

		# if not one of the 4 cases, return that it not a valid question
		else:
			return 'Invalid question. Please phrase your question into a who, what, when, or where format.'

		# placeholder for any articles
		art_found = ''

		# check the remaining words for articles
		# EX we start with "What is an apple?"
		#		by this point in the processing, we have topic = "an apple" 
		#		we want to remove "an" so we can run a search for a reformulated query "apple is"
		#		yet retain the article to answer "An apple is ..."
		for i, word in enumerate(topic):

			# if the current word is an article
			if word in art_list:

				# take the word out of the topic
				topic = topic[i+1:]

				# save the article
				art_found = word

				# stop, we don't want to override
				break

		# return a list with the broken up query along with return type, auxiliary words, and a looking back flag
		return [art_found, topic, q_verb, return_type, aux_word, looking_back]

	# method to take in a string and return a date in 'Month_name day_number, year_number' format
	def extract_date(self, string):

		# split the sentence on whitespace
		contents = string.split(' ')

		# store the original sentence in case no match is found
		result = string

		# loop through the words
		for i, word in enumerate(contents):

			# if the current word is a month
			month = self.month_check.search(word)
			if month:
				try: 
					# look for date in dd yyyy in the 2 words after the month. the comma is optional and gets removed
					#	ex November 29 2001
					if (date := re.search(r'(\d{1,2})\s+(\d{4})', f'{contents[i+1]} {contents[i+2]}'.replace(',', ' '))):

						# format date based on capture groups in the regex
						result = f'{month.group(0)} {date.group(1)}, {date.group(2)}'
						
						# exit the loop to avoid trying the other cases
						break

					# rare, but check if the date is in dd yyyy in the word to the left and right of the month
					# 	ex 4 April 1961
					elif (date := re.search(r'(\d{1,2})\s+(\d{4})', f'{contents[i-1]} {contents[i+1]}'.replace(',', ' '))):
						
						# format date based on capture groups in the regex
						result = f'{month.group(0)} {date.group(1)}, {date.group(2)}'

						# exit the loop to avoid trying the other cases
						break

					# if there is no year, only a day number in the next word
					#	ex December 25
					elif (date := re.search(r'(\d{1,2})', contents[i+1])):

						# format date based on capture group in the regex
						result = f'{month.group(0)} {date.group(1)}'

						# exit loop
						break
				except: pass

			# if a month is never found, we check for dd/mm/yyyy (or mm/dd/yyyy) format
			else:
				date = re.search(r'(\d{2}/\d{2}/\d{4})', word)
				if date:

					# grab the date from the regex
					result = date.group(0)

					# exit loop
					break

		# if a date was found, it will be returned, else the original string is returned
		return result

	# method to aid in checking for occurrences of patt1 and patt2 regexes given a page title
	def perform_extraction(self, title, patts, done, answer = False):
		
		# get the page specified by the given title, split into sentences
		content = w.page(title=title, auto_suggest=False).content.split('.')

		# loop through the sentences
		for sentence in content:

			# if the sentence is not empty and a match has not been found
			if sentence and not done:

				# loop through the patterns to check for
				for patt in patts:

					# look for the first pattern in the sentence
					match = patt.search(sentence)

					# if it was found and a match has not previously been found
					if match and not done:

						# store the answer
						answer = match.groups()[0]

						# write the occurrence in the log file
						self.log_file.write(f'\nSENTENCE FOUND: {sentence}\nUSING PATTERN:{patt}\nANSWER: {answer}\n')
						
						# set done flag
						done = True

		# return the done flag and the answer
		return done, answer

	# method to return the answer to the users question given the vector representation of the query
	def get_answer(self, question):

		# unpack the query list into its individual parts
		art_found, search_topic, q_verb, return_type, aux_word, looking_back = question

		# build a query list from the topic, verb, and auxiliary words
		query = search_topic + [q_verb] + aux_word.split(' ')

		# not done
		done = False

		# the base pattern 
		patt = ''.join([fr'\b{word}\b.*?' for word in query])

		# build the patts array, first pattern needs a capture group, so replace the last 3 characters of the base pattern
		patts = [patt[:-3] + r'(.*)\b,?']

		# if the looking back flag is set
		if looking_back:

			# add capture group to grab the rest of a phrase if a match is found
			patt1 = patt[:-3] + r'.*?((\w+\s*){1,})\b[\.,]'

			# grab the previous 1 to 3 words and convert the verb to passive mood
			patt2 = r'((\w+\s*){1,3})\b' + r'\b.*\b'.join([aux_word.split(' ')[0]]+search_topic)
			
			# patts array now has 2 different patterns to search for
			patts = [patt1, patt2]

		# precompile the regexes for ease of use later
		patts = list(map(re.compile, patts))

		# in an attempt to avoid making the query too broad, stop when the query is only 1 word or if an answer has been found
		while len(query) >= 2 and not done:

			# get a sentence from the query list
			search_query = ' '.join(query)

			# search wikipedia for page titles based on query 
			res = w.search(search_query)

			# if results were found and an answer has not been found
			if res and not done:

				# write the list of titles to the log file
				self.log_file.write(f'\nSEARCHED FOR: {search_query}\nTITLES OF PAGES RETURNED: {res}\n')
				
				# loop through the retrieved page titles
				for title in res:

					if not done:

						# can throw a disambiguation error if the title of the page is too ambiguous
						#	ex if my query is When did Thomas Edison die?, the search will become "Thomas Edison died on".
						#		As the query is shortened with each iteration of misses, the search query becomes "Thomas Edison"
						#		The page titles retrieved could include 'Edison High School'. The problem with this is that there 
						#		about 10 pages within wikipedia that match the title 'Edison High School' given the many schools with
						#		this name in the US. 
						try:
							done, answer = self.perform_extraction(title, patts, done, return_type)
						except Exception as e:

							# if the above threw an error, we update the query
							# this second search also has the capability to throw the same error
							try:

								# add the desired return type to the query (ex if Christmas caused this error, the new search is Christmas date)
								search_query += f'{return_type}'

								# search for matching documents
								res = w.search(search_query)

								# if a match has not been found and there were results returned
								if not done and res:

									# log the results
									self.log_file.write(f'\nSEARCHED FOR: {search_query}\nTITLES OF PAGES RETURNED: {res}\n')
									
									# loop through the titles
									for title in res:

										# if an answer has not been found
										if not done:

											# use the title to try to find the answer
											done, answer = self.perform_extraction(title, patts, done, return_type)
							
							# do nothing if an exception is thrown
							except Exception as e:
								pass
			# if no answer was found, it may be due to an overly specific query, 
			#	we retry the process with the last word removed. we do not change the patterns however
			query.pop(-1)
		
		# if we run out of queries and we don't find an answer, we return that it could not answer the question
		if not done:
			return 'I am sorry, I can not answer your question. Try a different question or rephrase.'
		
		# if we were looking for a date
		if return_type == 'date':

			# we get the date from the answer, which removes excess information
			answer = self.extract_date(answer)

			# it better have at leat one number in there or we didn't find a date and the question is not answered
			if not self.num_check.search(answer):
				return 'I am sorry, I can not answer your question. Try a different question or rephrase.'
		
		# combine the query list into the proper order and remove empty elements
		answer = list(filter(lambda i: i.strip(), [art_found, ' '.join(search_topic), q_verb, aux_word, answer.strip()]))
		
		# combine the answer into a sentence with a period
		answer = ' '.join(answer) + '.'

		# return the found answer
		return answer[0].upper() + answer[1:]

	# method to control the run of the q-a system
	def run(self):

		# starting string to be displayed at the beginning of the program
		begin_string = "*** This is a QA system by Jordan Dube. \n\tIt will try to answer questions that start with Who, What, When or Where.\n\tEnter 'exit' to leave the program.\n"
		
		# write it to the log file
		self.log_file.write(f'{begin_string}=?>\t')

		# get input question from the user
		question = input(begin_string + '=?>\t')
		
		# continue until the user types exit
		while 'exit' not in question:
			
			# log the question
			self.log_file.write(f'{question}\n')
			
			# process the question into a list
			question = self.process_question(question)

			# store the question
			answer = question

			# if the question is a list, then it was successful, if it isnt then it tells the user what was wrong with their query
			if type(question) == list:

				# use the question to get the answer
				answer = self.get_answer(question)

				# log the answer
				self.log_file.write(f'=>\t{answer}\n=?>\t')

			# get the next question from the user
			question = input(f'=>\t{answer}\n=?>\t')

		# log the exit message
		self.log_file.write('exit')

		# close the file handler
		self.log_file.close()

		# leave a message for the user
		print('Thank you! Have a nice day! :)')

# main method
def main():

	# get the args from the command line
	args = sys.argv[1:]

	# the log file is the only parameter provided
	log_file = args[0]

	# create QA object with the given filename
	qa = QA(log_file)

	# run the system
	qa.run()

# obligatory ifmain
if __name__ == '__main__':
	main()