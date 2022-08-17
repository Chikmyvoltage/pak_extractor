import struct
import sys
import argparse
from os import path, mkdir

parser = argparse.ArgumentParser( description='Extract .PAK file.' )
parser.add_argument('file', type=str, metavar='file', help='The .pak file to extract.')
parser.add_argument('--exdir', type=str, metavar='path', help='Extract to directory. Creates directories if not made already. Default value is pak_extractor_output_directory', default='pak_extractor_output_directory/')

args = parser.parse_args()

print(f"Opening file {args.file}")
fd = open(args.file, 'rb')



def read_pak_header(fd) -> dict:
	""" read_pak_header(fd) -> dict: Reads the stored file headers-
	inside the archive, creating a dictionary of filenames and their respected data lengths-
	to correctly read such file's data within the archive (file data chunks are adjacent)
	"""
	# Use reverse-engineered method.

	files_metadata   = {}
	amount_of_files ,= struct.unpack('>h', fd.read(2)) # unpacks the one-element tuple (x,)
       #(amount_of_files, ) = struct.unpack('>h', fd.read(2))

	for _ in range(amount_of_files):

		next_file_length ,= struct.unpack('>h', fd.read(2))

		file_name = fd.read(next_file_length).decode()

		data_length ,= struct.unpack('>h', fd.read(2))

		files_metadata[file_name] = data_length

	return files_metadata

# UTIL
def mkdirs(file_path : str) -> None:
	""" mkdirs(path : str) -> None: Mimicks the behaviour of `mkdir -p`. Creating parent directories when needed."""


	stripped = file_path.strip('/')
	p = stripped.partition('/')
	tmp = ""

	for _ in range( len( stripped.split('/') ) ): # each directory level in input

		tmp += p[0] + '/'
		if not path.isdir(tmp):
			mkdir(tmp)

		p = p[2].partition('/')
# END UTIL


out = '{file}'

if args.exdir:
	if args.exdir[-1] != '/':
		args.exdir += '/'

	if not path.isdir(args.exdir):

		try:
			mkdirs(args.exdir)
		except Exception as e:
			print(f"Couldn't create directory {args.exdir}", f"Reason: {e}", sep='\n')
			exit(2)

	out = '{dir}{file}'




files = read_pak_header(fd)
mlen = len( max(files, key=lambda x: len(x) ) ) # Returns the maximum character length out of all the keys

for key,val in files.items():
	p = out.format(dir=args.exdir, file=key)
	print(f"extracting {key:<{mlen}}... to {p}")
	with open(p, 'wb') as writer:
		writer.write(fd.read(val))


fd.close()
