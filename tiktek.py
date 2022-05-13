
from requests import Session
from json import loads, dumps

class TikTek:
	def __init__(self, timeout=10):
		self.timeout = 10
		self.url = "https://tiktek.com/"
		self.utils = TikTekUtils(
			url=self.url,
			timeout=self.timeout
		)

	def get_subjects(self):
		"""
		Returns a dictionary containing the name of a subject and its corresponding ID and image url on TikTek.
		"""
		return self.utils.get_subject_data()

	def get_book_id(self, book_name, subject=False, subject_id=False):
		"""
		Returns the string ID of a book.
		"""
		return self.get_book_data(
			book_name=book_name,
			subject=subject,
			subject_id=subject_id
		)["ID"]

	def download_book_pic(self, file_name, book_name, subject=False, subject_id=False):
		picture_data = self.utils.get(
			url=self.get_book_pic_url(
				book_name=book_name,
				subject=subject,
				subject_id=subject_id
			)
		).content
		f = open(file_name, "wb")
		fsize = f.write(picture_data)
		f.close()
		return fsize

	def get_book_pic_url(self, book_name, subject=False, subject_id=False):
		"""
		Returns the url to the book cover of a chosen book.
		"""
		return "{base_url}il/tt-resources-unmanaged/books-covers/{book_name}".format(
			base_url=self.url,
			book_name=self.get_book_data(
				book_name=book_name,
				subject=subject,
				subject_id=subject_id
			)["Image"]
		)

	def get_book_data(self, book_name, subject=False, subject_id=False):
		"""
		Returns a dictionary of information about a book.
		"""
		book_data = [data for data in self.get_books(
			subject=subject,
			subject_id=subject_id
		) if data['Title'].find(book_name) != -1]
		if book_data == []:
			raise TikTekError("Invalid book name.")
		return book_data[0]

	def get_books(self, subject=False, subject_id=False):
		"""
		Gets a list of all the books for a subject or a subject ID and all their data
		"""
		if not subject and not subject_id:
			raise TikTekError("No arguments supplied.")
		if subject and not subject_id:
			subject_data = self.get_subjects()
			guess = [data["id"] for subject_name, data in subject_data.items() if subject_name.find(subject) != -1]
			if guess == []:
				raise TikTekError("Invalid subject name.")
			subject_id = guess[0]
		self.utils.set_headers({
			"Accept": "application/json, text/javascript, */*; q=0.01",
			"Accept-Language": "en-US,en;q=0.9,en-CA;q=0.8,he;q=0.7",
			"Cache-Control": "no-cache",
			"Connection": "keep-alive",
			"Content-Type": "application/json; charset=UTF-8",
		})
		return loads(self.utils.post(url="https://tiktek.com/il/services/SolutionSearch.asmx/GetBooks", data=dumps({
			"locationID": None,
			"schoolID": None,
			"subjectID": subject_id
		})).text)["d"]["ResultData"]

	def download_solution(self, file_name, book_id, page, question):
		"""
		Downloads a solution to a file.
		"""
		picture_data = self.utils.get(
			url=self.get_solution_url(
				book_id, page, question
			)
		).content
		f = open(file_name, "wb")
		fsize = f.write(picture_data)
		f.close()
		return fsize

	def get_solution_url(self, book_id, page, question):
		"""
		Returns the url to the first solution given.
		"""
		solutions = self.get_solution_data(book_id, page, question)
		if solutions == []:
			return False
		return "{base_url}il/tt-resources/solution-images/{book_name}_{book_id}/{solution}".format(
			base_url=self.url,
			book_name=solutions[0]["Prefix"],
			book_id=solutions[0]["BookID"],
			solution=solutions[0]["Image"],
		)

	def get_solution_data(self, book_id, page, question):
		"""
		Returns the data of a question's solutions.
		"""
		self.utils.set_headers({
			"Accept": "application/json, text/javascript, */*; q=0.01",
			"Accept-Language": "en-US,en;q=0.9,en-CA;q=0.8,he;q=0.7",
			"Cache-Control": "no-cache",
			"Connection": "keep-alive",
			"Content-Type": "application/json; charset=UTF-8",
		})
		return loads(self.utils.post(url="https://tiktek.com/il/services/SolutionSearch.asmx/GetSolutionsEx", data=dumps({
			"bookID": book_id,
			"page": page,
			"question": question,
			"sq": None,
			"ssq": None,
			"userID": None
		})).text)["d"]["ResultData"]

	def get_subject_ids(self):
		"""
		Returns a list of the IDs of the subjects, without their names.
		"""
		return [data["id"] for book, data in self.utils.get_subject_data().items()]

class TikTekUtils:
	def __init__(self, url, timeout):
		self.url = url
		self.timeout = timeout
		self.s = Session()

	def set_headers(self, headers):
		self.s.headers.update(headers)

	def get_subject_data(self):
		self.set_headers({
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "en-US,en;q=0.9,en-CA;q=0.8,he;q=0.7",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
		})
		data = self.get(url=self.url, timeout=self.timeout)
		if data.status_code != 200:
			raise TikTokError("API Error")
		parse_subject_names = self.find_all(data.content.decode(), '" alt="', '"')
		start_index = parse_subject_names.index('מתמטיקה')
		end_index = parse_subject_names[start_index:].index('')
		subject_ids = [unclean_id.split("|")[-1] for unclean_id in self.find_all(data.content.decode(), '.png" title="', '"')[:end_index]]
		subject_names = parse_subject_names[start_index:start_index + end_index]
		subject_data = {}
		for i in range(len(subject_names)):
			subject_data[subject_names[i]] = {
				"id": subject_ids[i],
				"name": subject_names[i],
				"image": "https://tiktek.com/il/images/" + subject_ids[i] + ".png"
			}
		return subject_data

	def find_all(self, text, startToken, endToken):
		cases = []
		while True:
			if text.find(startToken) == -1 or text.find(endToken) == -1:
				break
			try:
				text = text[text.find(startToken) + len(startToken):]
				key = text[:text.find(endToken)]
				cases.append(key)
			except:
				break
		return cases

	def get(self, **kwargs):
		try:
			return self.s.get(**kwargs)
		except:
			raise TikTekError("Connection Error")

	def post(self, **kwargs):
		try:
			return self.s.post(**kwargs)
		except:
			raise TikTekError("Connection Error")

class TikTekError(Exception):
	pass
