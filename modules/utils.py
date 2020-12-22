import re
def str_word_count( string , format = 0 , charlist = '' ):
	if isinstance( string , str ):
		words = re.sub( '[^\w '+ charlist +']' , '' , string ) #Remove everything except alphanumeric, spaces and chars from charlist
		words = words.replace( '  ' , ' ' ).split( ' ' ) #Replacing double spaces with single space and creating list
		if format == 0:
			return len( words )
		elif format == 1:
			return words
		elif format == 2:
			result = {}
			for word in words:
				result[ string.find( word ) ] = word
			return result
	return False
def book_ids_from_links(book_link):
    return int(book_link.split('/')[2])
def stripslashes(string):
	return string.strip("/\\")
def url_join(*args):
	return "/".join(map(stripslashes,args))