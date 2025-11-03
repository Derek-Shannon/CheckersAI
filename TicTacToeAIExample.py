from random import randint
class Board:
	def __init__(self, board):
		self.board = [[],[],[]]
		for r in range(3):
			for c in range(3):
				self.board[r].append(board[r][c])
		self.blanks = self.getBlank()
	def place(self, type1, x, y):
		self.board[y][x] = type1
		self.blanks = self.getBlank()
	def print(self):
		print("  1 2 3")
		for r in range(3):
			printOut = ""+str(r+1)
			for c in range(3):
				printOut += " "+self.board[r][c]
			print(printOut)
	def getBlank(self):
		blank = []
		for row in range(3):
			for column in range(3):
				if self.board[row][column] == "-":
					blank.append([column,row])
		return blank
	def checkWin(self):
		for r in range(3):
			if self.board[r][0]==self.board[r][1] and self.board[r][0]==self.board[r][2]:
				if self.board[r][0] !="-":
					return True
		for c in range(3):
			if self.board[0][c]==self.board[1][c] and self.board[0][c]==self.board[2][c]:
				if self.board[0][c] !="-":
					return True
		if self.board[0][0] == self.board[1][1] and self.board[2][2] == self.board[0][0]:
			if self.board[0][0] !="-":
				return True
		if self.board[2][0] == self.board[1][1] and self.board[2][0] == self.board[0][2]:
			if self.board[2][0] !="-":
				return True

bObj1 = Board([["X","X","-"],
							 ["-","O","-"],
							 ["-","-","-"]])

class Tree:
	def __init__(self, par, b):
		self.parent = par
		self.boardObj = b
		self.children = []
		self.level = self.getLevel()
		self.win = self.boardObj.checkWin()
		self.score = 0
		if not self.win:
			blanks = self.boardObj.blanks
			if len(blanks) >0:# and self.level < 6:
				for i in range(len(blanks)):
					tempB = Board(self.boardObj.board)
					if self.level%2 == 0:
						tempB.place("O", blanks[i][0],blanks[i][1])
					else:
						tempB.place("X", blanks[i][0],blanks[i][1])
					self.children.append(Tree(self,tempB))
	def calculateScore(self):
		if self.level%2==1:
			return 10-self.level
		return self.level-10
	def minMax(self):
		if self.win:
			self.score = self.calculateScore()
			return self.score
		if len(self.boardObj.blanks)==0:# or self.level >= 6:
			self.score = 0
			return 0
		scores = []
		if self.children:
			for child in self.children:
				scores.append(child.minMax())
		if self.level%2==1:
			#print(" "*self.level+str(self.boardObj.board), min(scores))
			self.score = min(scores)
			return self.score
		else:
			#print(" "*self.level+str(self.boardObj.board), max(scores))
			self.score = max(scores)
			return self.score
	def count(self):
		global count
		count +=1
		if self.children:
			for child in self.children:
				child.count()
	def getLevel(self):
		level = 0
		p = self.parent
		while p:
			level += 1
			p = p.parent
		return level
	def print(self):
		spaces = "  " * self.level
		print(spaces+str(self.level) + str(self.boardObj.board))
		if self.children:
			for child in self.children:
				child.print()
class AI:
	def __init__(self):
		pass
	def turn(self, board):
		startNodeTree = Tree(None, board)
		best = startNodeTree.minMax()
		bestList = []
		for child in startNodeTree.children:
			if child.score == best:
				bestList.append(child.boardObj)
		return bestList[randint(0,len(bestList)-1)]