
from os import listdir
from os.path import isfile, join
import getpass, csv, datetime
import requests,json
import traceback, getpass, os
class ExtractPosts():
	graph_url = "https://graph.facebook.com/"
	user_post_code = "/tagged/"
	admin_post_code = "/posts/"
	access_token_URL = "?key=value&access_token=1435721096655907|0b60d3dad19ea239b967f4aed4118306"
	update_time = datetime.datetime.now().strftime("%y-%m-%d")
	dest_file_store = "/home/"+ getpass.getuser() + "/Facebook_Graph/" + "Results" + update_time + "/"
	def __init__(self, filePath=None):
		if not filePath:
			self.fb_id_filepath = "cvsfiles/"
		else:
			self.fb_id_filepath = filePath

	def get_posts(self):
		all_fb_codes = self.__getAllFBPageIDList(self.fb_id_filepath)
		for fb_code in all_fb_codes:
			fb_user_post_url = self.graph_url + fb_code + self.user_post_code + self.access_token_URL
			fb_admin_post_url = self.graph_url + fb_code + self.admin_post_code + self.access_token_URL
			self.__storePostsAndComments(fb_user_post_url, fb_code, "user")
			self.__storePostsAndComments(fb_admin_post_url, fb_code, "admin")

	def __storePostsAndComments(self, post_url, fb_code, poster):
		posts_content = []
		post_comment = []
		while post_url:
			url_response = self.__makeHTTPCall(post_url)
			url_response = json.loads(url_response)
			try:				
				all_response_data = url_response['data']
				for response_data in all_response_data:
					try:

						if poster == "admin":
							post_message = response_data['description']
						else:
							post_message = response_data['message']
						posts_content.append(post_message)
					except Exception, err:				
						print(traceback.format_exc())
					try:
						post_message_comment_list = response_data['comments']['data']
						for post_message_comment in post_message_comment_list:
							post_comment.append(post_message_comment['message'])
					except Exception, err:				
						print(traceback.format_exc())	
				post_url =  url_response['paging']['next']

			except Exception, err:				
				print(traceback.format_exc()), "Error with : ", post_url
				post_url = None
		posts_content_fileName = self.dest_file_store + fb_code + "/_message_" + poster + ".csv"
		posts_commentt_fileName = self.dest_file_store + fb_code + "/_comment_" + poster + ".csv"
		self.__storeListToCsv(posts_content, posts_content_fileName)
		self.__storeListToCsv(post_comment, posts_commentt_fileName)
		# return posts_content, post_comment

	def __storeListToCsv(self, content_list, filename):
		for content in content_list:
			self.writeToFile([content.encode('utf-8')],filename)


	def __makeHTTPCall(self, url):
		try:
			response = requests.get(url)
		except Exception, err:
			print(traceback.format_exc()), "Error", url

		return response.content

	def __getAllFBPageIDList(self, filepath):
		allIds = []
		for files in self.__getFileListFromFilePath(filepath):
			for row in self.__getListFromCSV(files):
				try:
					allIds.append(row[0])
				except:
					print row, " could not be appended"
		return allIds


	def __getFileListFromFilePath(self, filePath):
		onlyfiles = [ f for f in listdir(filePath) if isfile(join(filePath,f)) ]
		fileList = []
		for file in onlyfiles:
			if "readme" in file.lower():
				pass
			else:
				fileList.append(filePath + file)
		return fileList

	def __getListFromCSV(self, filename):
	    profileLinks = []
	    with open(filename, 'r') as f:
	        readColumns = (csv.reader(f, delimiter=','))
	        iter = 0
	        for row in readColumns:
	            profileLinks.append(row)
	        return profileLinks

	def writeToFile(self, row,destFile):
		if not os.path.exists(os.path.dirname(destFile)):
			os.makedirs(os.path.dirname(destFile))

		with open(destFile, 'a') as outcsv:			
			writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
			writer.writerow(row)

if __name__ == '__main__':
	extractPosts = ExtractPosts()
	extractPosts.get_posts()