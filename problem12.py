import json
from copy import deepcopy

###
#  To run this code
##


class Person:

	def __init__(self, name, gender):
		self.name = name
		self.gender = gender

	def __str__(self):
		return self.name

	def __eq__(self, other):
		return self.name == other.name


class FamilyTree:

	def __init__(self):
		self.relation_map = {}

	def add_person(self, name, gender):
		"""
		Adds a person to the tree.
		"""
		try:
			assert not self.relation_map.get(name, None), "Person already exists in the family"
			p = Person(name=name, gender=gender)

			# Intialize relation_map of person, i.e added to tree.
			self.relation_map[p.name] = self.relation_map.get(p.name, {"self": p})
			return p
		except AssertionError as e:
			return self.relation_map.get(name)['self']

	# ---------- Problem2 (Add Child to Family)-------------- #
	def __add_children(self, parent, children, relation=None):
		children = isinstance(children, list) or [children]

		if relation:
			self.relation_map[parent.name]['{0}s'.format(relation)] = self.relation_map[parent.name].get('{0}s'.format(relation), [])
			self.relation_map[parent.name]['{0}s'.format(relation)].extend(children)
		else:
			for child in children:
				relation = 'son' if child.gender == 'M' else 'daughter'
				self.relation_map[parent.name]['{0}s'.format(relation)] = self.relation_map[parent.name].get('{0}s'.format(relation), [])
				self.relation_map[parent.name]['{0}s'.format(relation)].append(child)

	def _add_parent_child_relation(self, parent, child, relation):
		"""
		Adds a Father<->Son, Father<->Daughter, Mother<->Son, Mother<->Daughter relationship
		between parent and child objects.
		"""

		# Add child to sons/daughters array of a particular parent
		self.__add_children(parent=parent, children=child, relation=relation)
		if parent.gender == 'M':
			# parent isFatherOf son
			self.relation_map[child.name]['father'] = parent

			# Add child to sons/daughters array of a particular parent's spouse.
			wife = self.relation_map[parent.name].get('wife', None)
			if wife:
				self.relation_map[child.name]['mother'] = wife
				self.__add_children(parent=wife, children=child, relation=relation)
		else:
			# parent isMotherOf son
			self.relation_map[child.name]['mother'] = parent

			# Add to sons/daughters array of a particular parent's spouse
			husband = self.relation_map[parent.name].get('husband', None)
			if husband:
				self.relation_map[child.name]['father'] = husband
				self.__add_children(parent=husband, children=child, relation=relation)

	def add_child(self, **kwargs):
		"""
		Add a child to the family tree.
		Can be called in the following ways
		- add_child(mother=person_name, daughter=person_name)
		- add_child(mother=person_name, son=person_name)
		- add_child(father=person_name, daughter=person_name)
		- add_child(father=person_name, son=person_name)
		"""
		try:
			assert len(kwargs.keys()) == 2, "No  of parameters to this function should be exactly 2."

			if kwargs.get('mother', None):
				assert (kwargs.get('daughter', None) or kwargs.get('son', None)), "Next parameter should be son or daughter"
				parent = Person(name=kwargs['mother'], gender='F')
			else:
				assert (kwargs.get('daughter', None) or kwargs.get('son', None)), "Next parameter should be son or daughter"
				parent = Person(name=kwargs['father'], gender='M')

			assert self.relation_map[parent.name], "Parent should exist before adding child."
			if kwargs.get('daughter', None):
				child = self.add_person(name=kwargs['daughter'], gender='F')
				self._add_parent_child_relation(parent, child, 'daughter')
			else:
				child = self.add_person(name=kwargs['son'], gender='M')
				self._add_parent_child_relation(parent, child, 'son')
		except AssertionError as e:
			raise e
	# ---------- End Problem2 -------------- #

	def add_couple(self, husband, wife):
		"""
		Adds an husband<->wife couple to the tree, and update their children.
		"""
		try:
			husband = self.add_person(husband, gender='M')
			wife = self.add_person(wife, gender='F')

			# Add relation and it's corresponding inverse.
			self.relation_map[wife.name]['husband'] = husband
			self.relation_map[husband.name]['wife'] = wife

			# Update child relations.
			w_children = self.get_children(wife)
			h_children = self.get_children(husband)
			if w_children and not h_children:
				self.__add_children(parent=husband, children=w_children)
			elif h_children and not w_children:
				self.__add_children(parent=wife, children=h_children)
		except AssertionError as e:
			raise e

	def serialize(self):
		"""
		Serialize the relationmap to json for better viewing
		:return:
		"""
		serialized_dict = deepcopy(self.relation_map)

		for person_name, person_obj in serialized_dict.items():
			for relation in person_obj:
				persons = person_obj[relation]
				if isinstance(persons, list):
					serialized_array = []
					for person in persons:
						p = {}
						p.update(person.__dict__)
						serialized_array.append(p)
					serialized_dict[person_name][relation] = serialized_array
				else:
					p = {}
					p.update(persons.__dict__)
					serialized_dict[person_name][relation] = p
		return json.dumps(serialized_dict)

	###### Relation functions
	def get_father(self, person):
		return self.relation_map[person.name].get('father', None)

	def get_mother(self, person):
		return self.relation_map[person.name].get('mother', None)

	def get_sons(self, person):
		return self.relation_map[person.name].get('sons', [])

	def get_daughters(self, person):
		return self.relation_map[person.name].get('daughters', [])

	def get_spouse(self, person):
		if person.gender == 'F':
			return self.relation_map[person.name].get('husband', None)
		return self.relation_map[person.name].get('wife', None)

	def get_brothers(self, person):
		father = self.get_father(person)
		mother = self.get_mother(person)

		# Try get sons from both mother or father.
		sons = []
		sons.extend((father and self.get_sons(father) or []) or (mother and self.get_sons(mother) or []))
		try:
			sons.remove(person)
		except ValueError:
			pass
		return sons

	def get_sisters(self, person):
		father = self.get_father(person)
		mother = self.get_mother(person)

		# Try get daughter from both mother or father.
		daughters = []
		daughters.extend((father and self.get_daughters(father) or []) or (mother and self.get_daughters(mother) or []))
		try:
			daughters.remove(person)
		except ValueError:
			pass
		return daughters

	def get_children(self, person):
		return self.get_sons(person) + self.get_daughters(person)

	def get_siblings(self, person):
		return self.get_brothers(person) + self.get_sisters(person)

	def get_cousins(self, person):
		father = self.get_father(person)
		mother = self.get_mother(person)
		paternal_siblings = (father and self.get_siblings(father) or [])
		maternal_siblings = (mother and self.get_siblings(mother) or [])
		cousins = []
		for sibling in paternal_siblings + maternal_siblings:
			cousins.extend(self.get_children(sibling))
		return cousins

	def get_grandsons(self, person):
		grandsons = []
		for child in self.get_children(person):
			grandsons.extend(self.get_sons(child))
		return grandsons

	def get_granddaughters(self, person):
		granddaughters = []
		for child in self.get_children(person):
			granddaughters.extend(self.get_daughters(child))
		return granddaughters

	def get_grandchildren(self, person):
		return self.get_grandsons(person) + self.get_granddaughters(person)

	def get_brother_in_laws(self, person):
		spouse = self.get_spouse(person)
		spouse_brothers = spouse and self.get_brothers(spouse) or []

		sisters = self.get_sisters(person) or []
		husbands_of_sisters = []
		for sister in sisters:
			husbands_of_sisters.append(self.get_spouse(sister))
		return husbands_of_sisters + spouse_brothers

	def get_sister_in_laws(self, person):
		spouse = self.get_spouse(person)
		spouse_sisters = (spouse and self.get_sisters(spouse)) or []

		brothers = self.get_brothers(person) or []
		wives_of_brothers = []
		for brother in brothers:
			wives_of_brothers.append(self.get_spouse(brother))
		return wives_of_brothers + spouse_sisters

	def get_maternal_uncle(self, person):
		mother = self.get_mother(person)
		return mother and (self.get_brothers(mother) + self.get_brother_in_laws(mother)) or []

	def get_paternal_uncle(self, person):
		father = self.get_father(person)
		return father and (self.get_brothers(father) + self.get_brother_in_laws(father)) or []

	def get_maternal_aunt(self, person):
		mother = self.get_mother(person)
		return mother and (self.get_sisters(mother) + self.get_sister_in_laws(mother)) or []

	def get_paternal_aunt(self, person):
		father = self.get_father(person)
		return father and (self.get_sisters(father) + self.get_sister_in_laws(father)) or []


# ---------- Problem 1 Find relative ---------------- #
	def find_relative(self, person, relation):
		person = self.relation_map[person]['self']
		if relation == 'mother':
			mother = self.get_mother(person)
			return mother and mother.name
		if relation == 'father':
			father = self.get_father(person)
			return father and father.name
		elif relation == 'son':
			return ', '.join([o.name for o in self.get_sons(person)])
		elif relation == 'daughter':
			return ', '.join([o.name for o in self.get_daughters(person)])
		elif relation == 'cousin':
			return ', '.join([o.name for o in self.get_cousins(person)])
		elif relation == 'children':
			return ', '.join([o.name for o in self.get_children(person)])
		elif relation == 'brothers':
			return ', '.join([o.name for o in self.get_brothers(person)])
		elif relation == 'sisters':
			return ', '.join([o.name for o in  self.get_sisters(person)])
		elif relation == 'grandsons':
			return ', '.join([o.name for o in  self.get_grandsons(person)])
		elif relation == 'granddaughters':
			return ', '.join([o.name for o in self.get_granddaughters(person)])
		elif relation == 'grandchildren':
			return ', '.join([o.name for o in self.get_grandchildren(person)])
		elif relation == 'brother-in-law':
			return ', '.join([o.name for o in self.get_brother_in_laws(person)])
		elif relation == 'sister-in-law':
			return ', '.join([o.name for o in self.get_sister_in_laws(person)])
		elif relation == 'maternal-uncle':
			return ', '.join([o.name for o in self.get_maternal_uncle(person)])
		elif relation == 'paternal-uncle':
			return ', '.join([o.name for o in self.get_paternal_uncle(person)])
		elif relation == 'maternal-aunt':
			return ', '.join([o.name for o in self.get_maternal_aunt(person)])
		elif relation == 'paternal-aunt':
			return ', '.join([o.name for o in self.get_paternal_aunt(person)])


# ---------- Problem 1 Fill family tree---------------- #
def fillFamilyTree():
	"""
	Creates a new family tree object and fills it with members.
	"""

	fTree = FamilyTree()
	# First Level
	fTree.add_couple(husband='Shan', wife='Anga')
	# End First level

	## Second Level
	fTree.add_child(father='Shan', son='Ish')
	fTree.add_child(father='Shan', son='Chit')
	fTree.add_child(father='Shan', son='Vich')
	fTree.add_child(father='Shan', daughter='Satya')


	fTree.add_couple(husband="Chit", wife="Ambi")
	fTree.add_couple(husband="Vich", wife="Lika")
	fTree.add_couple(husband="Vyan", wife="Satya")
	## End Second level


	### Third level
	fTree.add_child(father="Chit", son="Drita")
	fTree.add_child(father="Chit", son="Vrita")
	fTree.add_child(father="Vich", son="Vila")
	fTree.add_child(father="Vich", daughter="Chika")
	fTree.add_child(father="Satya", daughter="Satvy")
	fTree.add_child(father="Satya", son="Savya")
	fTree.add_child(father="Satya", son="Sayaan")

	fTree.add_couple(husband="Drita", wife="Jaya")
	fTree.add_couple(husband="Vila", wife="Jnki")
	fTree.add_couple(husband="Kpilla", wife="Chika")
	fTree.add_couple(husband="Asva", wife="Satvy")
	fTree.add_couple(husband="Savya", wife="Krpi")
	fTree.add_couple(husband="Sayaan", wife="Mina")
	### End Third level

	#### Fourth Level
	fTree.add_child(father="Drita", son="Jata")
	fTree.add_child(father="Drita", daughter="Driya")
	fTree.add_child(father="Vila", daughter="Lavnya")
	fTree.add_child(father="Savya", son="Kriya")
	fTree.add_child(father="Sayaan", son="Misa")

	fTree.add_couple(husband="Mnu", wife="Driya")
	fTree.add_couple(husband="Gru", wife="Lavnya")
	#### End Fourth Level

	return fTree

# ---------- Problem 1 ---------------- #



### Sample Problems ###
if __name__ == '__main__':
	fTree = fillFamilyTree()
	# 1. (MEET THE FAMILY)
	print("Problem1")
	print(fTree.find_relative(person="Ish", relation="brothers"))
	# End 1.

	#2. (A NEW BORN)
	print("Problem2")
	fTree.add_child(mother="Lavnya", daughter="Vanya")
	print(fTree.find_relative(person="Jnki", relation="grandchildren"))
	# End2.
################