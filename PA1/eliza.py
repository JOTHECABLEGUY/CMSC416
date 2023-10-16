## Eliza program ##
# Implemented by Jordan Dube for PA 1 for CMSC 416 w/ Prof. McInnes
# Credit to Weizenbaum for developing the original ELIZA program and providing insights into how it works #
# Python 3.9.12
# usage: python eliza.py

# 	The problem is that machines need to be able to simulate human interaction. This program and the program it is based off of
# 		is marks a big step in this direction. Without actual comprehension, conversation can be simulated through simple questions
#		and hard-coded comments to continue conversation. 

##	Example run:
##		python eliza.py
##			# eliza screen is printed
##		[ELIZA] >> HELLO, I AM ELIZA, YOUR PSYCHOTHERAPIST. WHAT IS YOUR NAME?
##  		[???] >> Jordan
## 		[ELIZA] >> WHAT CAN I HELP YOU WITH TODAY, JORDAN?
##  		[JORDAN] >> I am sad
## 		[ELIZA] >> IS ANYTHING IN PARTICULAR CAUSING YOU TO BE SAD
##  		[JORDAN] >> I think it was caused by my dream last night
## 		[ELIZA] >> TELL ME MORE ABOUT THIS DREAM, JORDAN.
##  		[JORDAN] >> I dreamed that I was on a boat
## 		[ELIZA] >> TELL ME MORE ABOUT THIS DREAM, JORDAN.
##  		[JORDAN] >> it was so cold and I was scared
## 		[ELIZA] >> I SEE.
##  		[JORDAN] >> We hit an iceberg and just as i was about to drown, i woke up
## 		[ELIZA] >> I REMEMBER YOU MENTIONING BOAT, JORDAN, COULD YOU TELL ME MORE ABOUT IT?
##  		[JORDAN] >> it was too dark, but it looked like the titanic
## 		[ELIZA] >> I SEE.
##  		[JORDAN] >> what do think it means?
## 		[ELIZA] >> I SEE.
##  		[JORDAN] >> what do you think it means?
## 		[ELIZA] >> WHY ARE YOU CONCERNED WITH ME?
##  		[JORDAN] >> I guess i crave human interaction
## 		[ELIZA] >> WHY DO YOU CRAVE HUMAN INTERACTION?
##  		[JORDAN] >> because i have never had any friends before
## 		[ELIZA] >> CAN YOU THINK OF SOMETHING IN PARTICULAR?
##  		[JORDAN] >> i guess it started when i was in middle school and my friends formed a group without me
## 		[ELIZA] >> I REMEMBER YOU MENTIONING CRAVE, JORDAN, COULD YOU TELL ME MORE ABOUT IT?
##  		[JORDAN] >> i want to feel wanted
## 		[ELIZA] >> WHAT DOES IT MEAN TO YOU TO FEEL WANTED?
##  		[JORDAN] >>
## 		Exiting. Thank you for the chat, JORDAN! :)

### This program simulates a Rogerian psychotherapist by taking input lines from the user, making substitutions
### 	to ease processing, decomposing the input according to preset decomposition rules, and formulating a response
###		based on the chosen decomposition format. The program also possess rudimentary memory to recall topics brought
###		up by the user in previous input lines. The program operates in an infinite loop, but terminates on empty input 
###		or a CTRL+C from the user. No command line arguments are needed/used. Implementation choices were made by 
###		consulting the work of Weizenbaum and personal preference.

# imports
from re import match, search, sub, split
from sys import exit
from random import randint, choice
from time import sleep

# ELIZA class 
class Eliza:

	# method to format lines to be printed to the terminal
	# takes a string line to be formatted
	# returns the formatted string 
	def format_out_line(self, line):
		return f'[ELIZA] >> {line}\n [{self.user_name}] >> '.upper()

	# method to print a credits screen, prints the name of the program as well as development credit
	def print_credits(self):
		print('ψ'*105)
		print('ψ'*105, '\n')
		print(' '*4, 'ψ', ' '*14, 'ψ', ' '*14, 'ψ', ' '*14, 'ψ', ' '*14, 'ψ', ' '*23, 'ψ')
		print(' '*3, 'ψ'*3, ' '*12, 'ψ'*3, ' '*12, 'ψ'*3, ' '*12, 'ψ'*3, ' '*12, 'ψ'*3, ' '*21, 'ψ'*3)
		print(' '*4, 'ψ', ' '*14, 'ψ', ' '*14, 'ψ', ' '*14, 'ψ', ' '*14, 'ψ', ' '*23, 'ψ')
		print(' '*8,'ψ'*10, ' '*5, 'ψψ', ' '*13, 'ψ'*10, ' '*5, 'ψ'*10, ' '*14, 'ψ', ' '*5)
		print(' '*8,'ψ'*10, ' '*5, 'ψψ', ' '*13, 'ψ'*10, ' '*5, 'ψ'*10, ' '*13, 'ψ'*3,' '*4)
		print(' '*8,'ψ'*2, ' '*13, 'ψψ', ' '*17, 'ψ'*2, ' '*16, 'ψ'*2, ' '*13, 'ψ'*2, 'ψ'*2,' '*4)
		print(' '*8,'ψ'*2, ' '*13, 'ψψ', ' '*17, 'ψ'*2, ' '*15, 'ψ'*2, ' '*13, 'ψ'*2, ' '*1, 'ψ'*2)
		print(' '*8,'ψ'*10, ' '*5, 'ψψ', ' '*17, 'ψ'*2, ' '*14, 'ψ'*2, ' '*13, 'ψ'*9, ' '*2)
		print(' '*8,'ψ'*10, ' '*5, 'ψψ', ' '*17, 'ψ'*2, ' '*13, 'ψ'*2, ' '*13, 'ψ'*11, ' '*2)
		print(' '*8,'ψ'*2, ' '*13, 'ψψ', ' '*17, 'ψ'*2, ' '*12, 'ψ'*2, ' '*13, 'ψ'*2, ' '*7, 'ψ'*2)
		print(' '*8,'ψ'*2, ' '*13, 'ψψ', ' '*17, 'ψ'*2, ' '*11, 'ψ'*2, ' '*13, 'ψ'*2, ' '*9, 'ψ'*2)
		print(' '*8,'ψ'*10, ' '*5, 'ψ'*10, ' '*5, 'ψ'*10, ' '*5, 'ψ'*10, ' '*6, 'ψ'*2, ' '*11, 'ψ'*2)
		print(' '*8,'ψ'*10, ' '*5, 'ψ'*10, ' '*5, 'ψ'*10, ' '*5, 'ψ'*10, ' '*5, 'ψ'*2, ' '*13, 'ψ'*2)
		print(' '*4, 'ψ', ' '*14, 'ψ', ' '*14, 'ψ', ' '*14, 'ψ', ' '*14, 'ψ', ' '*23, 'ψ')
		print(' '*3, 'ψ'*3, ' '*12, 'ψ'*3, ' '*12, 'ψ'*3, ' '*12, 'ψ'*3, ' '*12, 'ψ'*3, ' '*21, 'ψ'*3)
		print(' '*4, 'ψ', ' '*14, 'ψ', ' '*14, 'ψ', ' '*14, 'ψ', ' '*14, 'ψ', ' '*23, 'ψ', '\n')
		print("~ "*18, 'Implementation by Jordan Dube ', '~ '*18)
		print(' ~'*18, 'Based on work by J. Weizenbaum', ' ~'*18, '\n')
		print('ψ'*105)
		print('ψ'*105, '\n')

	# constructor for the Eliza class
	def __init__(self):

		self.print_credits() 	# print the credit screen as implemented above
		self.tobe_found = False # flag to determine if a form of the verb to be is found
		self.user_line = '' 	# initialize the variable to hold user input
		self.user_name = "???" 	# initialize the name of the user
		self.key_stack = [] 	# initialize the list to keep track of the key words and weights found in the user_line
		self.memory = set() 	# initialize the memory to allow ELIZA to recall from previous prompts

		# print the welcome statement from Eliza to get the user's name 
		self.out_line = self.format_out_line("Hello, I am ELIZA, your psychotherapist. What is your name?")
		
		# create a dictionary to store possible pronouns that will be encountered and their corresponding substitutions 
		self.pronoun_sub_dict = {r'\bi\b':'you', r'\bme\b':'you', r'\byou\b':'i', r'\bmy\b':'your', r'\byour\b':'my', r'\byourself\b': 'myself', r'\bmyself\b': 'yourself'}
		
		# pronouns will be handled by the pronoun_sub_dict, forms of the verb to be will be converted according to the key-value pairs in the tobe_sub_dictionary
		self.tobe_sub_dict = {r'\bare\b':'am', r'\bam\b':'are'}
		
		# this dictionary stores the mappings of contractions to their expanded forms
		self.contraction_dict = {r"\bwon'?t\b": 'will not', r"\bdon'?t\b": 'do not', r"\bdidn'?t\b": 'did not', 
								r"\byou'?re\b":'you are', r"\bi'?m\b": 'i am', r"\bcan'?t\b":'can not'}
		
		# get the username from the user
		self.user_name = input(self.out_line).upper().strip()
		
		# if no input is provided, exit the program
		if not self.user_name:
			print("No name provided, exiting. Thank you for chatting! :)")
			exit()

		# output the second intro line to start the conversation
		self.out_line = self.format_out_line(f'What can I help you with today, {self.user_name}?')
		
		# decomposition rules: keys are in (root, weight) form, Weights are arbitrary, 
		#	values are lists of lists. Each list within the list of values is the form 
		#	[[regex, possible responses, to input that matches, the regex], 
		#	[2nd regex for same root word, x, y, z]]. some root words have slightly different
		#	meanings or responses based on the surrounding words, so multiple decomposition regexes 
		#	are used to accommodate this. Spot words: Dream, remember, crav, belie, boat, think, learn,
		#	and feel. Other words have decomposition rules to add variety to the output.
		self.decomp_rules = {('dream', 10): [[r'.*\bdream((ed)|(s)|(ing))?\sabout\b(.+)', f'{self.user_name}, do you often dream about (2)?', r"Tell me more about this dream.", r"Does this dream suggest anything to you?"], [r"\bdream((ed)|(s)|(ing))?\b", f"Tell me more about this dream, {self.user_name}.", r"Does this dream suggest anything to you?"]],
							 ('remember', 9):[[r'\bdo\si\sremember\b(.+)', f'yes, {self.user_name}, i do remember (1).', 'did you think i would forget?'], [r'\byou.*do not.*remember\b', "Let us move on for now."], [r'\byou.*remember(ed)?(.+)', r"can you tell me more about (2)?"]],
							 ('yes', 8): [[r'\byes\b', 'you sound sure.', 'good, your tone suggests positivity.']],
							 ('no', 7): [[r'\bno\b', f'are you sure, {self.user_name}?', 'your tone suggests negativity', 'are you just saying no to be contrary?']],
							 ('crav', 6): [[r'\byou\b.*\bcrav((e)|(ing)|(ed))(.+)', r'Why do you crave (2)?', r'What would it mean to you to obtain (2)?', 'tell me more about this craving.']],
							 ('belie', 5): [[r'\byou\b.*\bbeliev((e)|(ing)|(ed))\s((in)|(that))?(.+)', f'{self.user_name}, can you tell me more about your belief in (3)?', r'How important is (3) to you?'], [r'\bbelief\b', 'Tell me more about this belief.']],
							 ('any', 4): [[r'\bany(.+)', r'Can you think of something in particular?']],
							 ('every', 3): [[r'\bevery(.+)', r'Can you think of a specific example?']],
							 ('all', 2): [[r'\ball\b(.+)', f'{self.user_name}, can you think of a specific example?']],
							 ('boat', 1): [[r'\bboats?\b', r'Tell me more about boats.', r'What comes to mind when you think about a boat?']],
							 ('think', 0): [[r'\byou\b.*\bthink(ing)?\b.*\bthat\b(.+)', r'What makes you think that (2)?', r'How does (2) affect you?'], [r'\bthink(ing)?\b.*((of)|(about))(.+)\b', r'How does thinking about (3) make you feel?', f'{self.user_name}, can you elaborate about (3)?']],
							 ('thought', 0): [[r'\byou\b.*\bthought\b.*\bthat\b(.+)', r'What makes you think that (1)?', r'How does (1) affect you?'], [r'\bthought\b.*((of)|(about))(.+)\b', r'How does thinking about (2) make you feel?', f'{self.user_name}, can you elaborate about (2)?']],
							 ('eat', -1): [[r'\beat(ing)?\b(.+)', r"How do you feel about (2)?", r'Tell me about your favorite foods.']],
							 ('ate', -1): [[r'\bate\b(.+)', r"How do you feel about (1)?", r'Tell me about your favorite foods.', r'What feelings came to mind when eating (1)?']],
							 ('learn', -2): [[r'\blearn((ed)|(ing))?\s((that)|(about)|(of))\s(.+)', r"what have you learned about (3)?", f"{self.user_name}, what do you feel when thinking about (3)?"], [r'\blearn((ed)|(ing))?\s(.+)', r"what have you learned about (2)?", f"{self.user_name}, what do you feel when thinking about (2)?"]],
							 ('good', -3): [[r'\bgood\b', "I see that you consider this in a positive light. Care to explain further?"]],
							 ('bad', -4): [[r'\bbad\b', "I see that you consider this in a negative light. Care to explain further?"]],
							 ('feel', 11): [[r'\byou.*(are)?((feeling)|(feel))\s(.+)', r"What does it mean to you to feel (3)?", f"{self.user_name}, do you want to talk about feeling (3)?", r"Why do you feel (3)?"]]}
		
		# this list contains regexes of keys that should be added to memory if they appear in user input (only added if there is a key with a higher weight in the input line)
		self.mem_keys = [r'dream', r'crav(e|ing)', r'belie(ve|ving|f)', r'boats?', r'eat(ing)?', r'learn(ing)?']
	
	# method to process the user provided line. Takes care of substitution, decomposition, 
	#	and choosing the response for inputs that contain keys with decomposition rules
	def process(self):

		line = self.user_line.lower() 						# avoid case conflicts
		
		# expand the contractions defined in the contraction_dict
		for k,v in self.contraction_dict.items():
			line = sub(k, v, line)

		# cleanse certain punctuations that may interfere with the \b escape character in regexes
		line = sub(r';', ' ', line)
		line = sub(r',', ' ', line)
		line = sub(r'\.', ' ', line)
		line = sub(r'\?', ' ', line)
		line = sub(r'!', ' ', line)

		# split the line along word boundaries and only store the resulting elements if they are not empty
		line = [token.strip() for token in split(r'\b', line) if token.strip()]
		pronoun_keys = list(self.pronoun_sub_dict.keys()) 	# simplify the name of the keys for readability
		tobe_keys = list(self.tobe_sub_dict.keys()) 		# simplify the name of the keys for readability
		
		# loop through the line of words
		for word_index in range(len(line)):

			# loop through the pronoun dict keys
			for key_index in range(len(pronoun_keys)):

				# check for a match, meaning the current word is the current pronoun
				if (p_match := match(pronoun_keys[key_index], line[word_index])):

					# change the pronoun found within the list and go to the next word
					line[word_index] = sub(p_match[0], self.pronoun_sub_dict[pronoun_keys[key_index]], line[word_index])
					break

			# loop through the "to be" keys
			for key_index in range(len(tobe_keys)):

				# check for a match, meaning that the current word is a form of "to be"
				if (tb_match := match(tobe_keys[key_index], line[word_index])):

					# substitute the word to the correct form for responding then go to the next word
					line[word_index] = sub(tb_match[0], self.tobe_sub_dict[tobe_keys[key_index]], line[word_index])
					self.tobe_found = True # set the flag that say that "to be" was found
					break

			# loop through the keywords that will be saved to memory
			for key_index in range(len(self.mem_keys)):
				if (m := search(self.mem_keys[key_index], line[word_index])):
					self.memory.add((m[0], self.mem_keys[key_index]))

		self.user_line = " ".join(line) 			# recombine the line into a single space-delimited string
		decomps = list(self.decomp_rules.keys()) 	# simplify the name of the keys for readability
		
		# loop through each decomposition list
		for decomp in decomps:

			# check for a match meaning that the keyword if found in the user_line
			if (d_match := search(decomp[0], self.user_line)):

				# when a match is found, need to identify the form it is in, done by
				#	looping and checking each regex for the given keyword to find a match
				for decomp_rule in self.decomp_rules[decomp]:
					if (dr_match := search(decomp_rule[0], self.user_line)):

						# when a match is found, make a random choice of the response
						response_choice = choice(decomp_rule[1:])
						dr_match = dr_match.groups() # groups is used for identifying the words dynamically used in the response
						
						# if there are groups present, take the last group and substitute it into the chosen response
						#	this method is based on how i set up my decomp rules, with only 1 group being used per response
						if len(dr_match) > 0 and dr_match[-1]:
							response_choice = sub(r'\(\d\)', dr_match[-1].strip(), response_choice)

						# add the keyword, the weight, and the chosen response to the keystack
						self.key_stack.append([decomp[0], decomp[1], response_choice])
		
		# sort the keystack according to reversed weight, so the first index is associated with the highest weight
		self.key_stack.sort(key = lambda decomp_tuple: int(decomp_tuple[1]), reverse = True)
	
	# method to handle responding to the user
	def respond(self):

		# if keywords were found, then the key stack will be populated
		if len(self.key_stack) > 0:
			
			current_key_entry = self.key_stack[0] 	# the key that will be processed is at index 0 because the stack was sorted according to inverse weight
			self.user_line = current_key_entry[-1] 	# line to be formatted is the response that was already altered in self.process()
			
			# remove the key from memory because it has already been processed. Need to loop because there are different forms the keys can take (boat v. boats)
			memory_to_remove = [mem for mem in self.memory if search(mem[1], current_key_entry[0])]
			for element in memory_to_remove:
				self.memory.discard(element)

		# if the user attempts to ask about Eliza or talk about her, redirects back to the user
		elif search(r'\bi\b', self.user_line):
			self.user_line = choice(["Let us talk about you, not me.", f"I would prefer to focus on you, {self.user_name}.", 'Why are you concerned with me?'])
		
		# If keys exist in memory. A random number 1-10 is also used to add variety to the program
		elif self.memory and randint(1, 10) > 5:

			mem_choice = choice(list(self.memory)) 	# choose one of the keys in memory

			# set the user_line to a response that shows that Eliza remembers the previous keys
			self.user_line = f'I remember you mentioning {mem_choice[0]}, {self.user_name}, could you tell me more about it?'
			self.memory.discard(mem_choice) 		# remove the key from memory to avoid asking about it twice
		
		# if the verb "to be" was found, randomly choose a response format (all questions) and alter the verb to be accordingly
		elif self.tobe_found:

			self.user_line = choice([sub(r'\byou.*are\b', r'are you', f'Why {self.user_line}'),
									sub(r'\bam\b', 'to be', sub(r'\bare\b', r'to be', f'What does it mean to {self.user_line}')),
									sub(r'\bam\b', 'to be', sub(r'\bare\b', r'to be', f'Is anything in particular causing {self.user_line}'))])
		
		else:
			# pick an ambiguous option, including a reworded input and a request for additional information
			self.user_line = choice([self.user_line, 'I see.', f'Please continue, {self.user_name}.', f"I am not entirely sure what you mean, {self.user_name}.", "I do not understand.", "Can you reprase that?"])
		
		self.key_stack = [] 									# reset the key_stack for the next line
		self.tobe_found = False 								# unset the to be flag
		self.out_line = self.format_out_line(self.user_line) 	# format the line to be output 
	
	# method to handle control of Eliza
	def run(self):

		# infinite loop to keep the conversation going until the user does not provide input or a SIGINT/KILL is raised
		while True:

			self.user_line = input(self.out_line) 	# get new input from the user

			# exit if nothing provided
			if not self.user_line:
				print(f"Exiting. Thank you for the chat, {self.user_name}! :)")
				exit()

			self.process() 							# process the input
			self.respond() 							# respond based on processed input
			sleep(1)

# main method			
def main():

	eliza = Eliza() # make an instance of Eliza by calling constructor (__init__)
	eliza.run() 	# call the run method of the eliza class

# obligatory ifmain to call the main function
if __name__ == '__main__':
	main()
