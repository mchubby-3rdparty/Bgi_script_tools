#!/usr/bin/env python3

# BGI script inserter

import glob
import os
import re
import struct
import sys

import bgi_common
import bgi_setup

re_line = re.compile(r'<(\d+?)>(.*)')

def get_text(fi, ilang):
	re_line = re.compile(r'<(\w\w)(\w)(\d+?)>(.*)')
	texts = {}
	for line in fi:
		line = line.rstrip('\n')
		if re_line.match(line):
			lang, marker, id, text = re_line.match(line).groups()
			id = int(id)
			if lang == ilang:
				record = marker, id
				texts[record] = bgi_common.unescape(text)
	return texts
	
def insert_unique(code_bytes, code_section, texts, text_bytes, imarker):
	text_dict = {}
	code_size = len(code_bytes)
	offset = len(text_bytes)
	for addr in  sorted(code_section):
		text, id, marker, comment = code_section[addr]
		if marker == imarker:
			if text in text_dict:
				marker, id, doffset = text_dict[text]
				code_bytes[addr:addr+4] = struct.pack('<I', doffset+code_size)
			else:
				ntext = texts[(marker,id)]
				nbytes = ntext.encode(bgi_setup.ienc) + b'\x00'
				text_bytes += nbytes
				text_dict[text] = marker, id, offset
				code_bytes[addr:addr+4] = struct.pack('<I', offset+code_size)
				offset += len(nbytes)
	return text_bytes
	
def insert_sequential(code_bytes, code_section, texts, text_bytes, imarker):
	code_size = len(code_bytes)
	offset = len(text_bytes)
	for addr in sorted(code_section):
		text, id, marker, comment = code_section[addr]
		if marker == imarker:
			ntext = texts[(marker,id)]
			nbytes = ntext.encode(bgi_setup.ienc) + b'\x00'
			text_bytes += nbytes
			code_bytes[addr:addr+4] = struct.pack('<I', offset+code_size)
			offset += len(nbytes)
	return text_bytes
	
def insert_script(odir, script, ilang):
	data = open(script, 'rb').read()
	hdr_bytes, code_bytes, text_bytes, config = bgi_common.split_data(data)
	text_section = bgi_common.get_text_section(text_bytes)
	code_section = bgi_common.get_code_section(code_bytes, text_section, config)
	texts = get_text(open(script+bgi_setup.dext, 'r', encoding=bgi_setup.denc), ilang)
	code_bytes = bytearray(code_bytes)
	text_bytes = b''
	text_bytes = insert_unique(code_bytes, code_section, texts, text_bytes, 'N')        # names
	text_bytes = insert_sequential(code_bytes, code_section, texts, text_bytes, 'T')    # text
	text_bytes = insert_unique(code_bytes, code_section, texts, text_bytes, 'Z')        # other
	fo = open(os.path.join(odir,os.path.split(script)[1]), 'wb')
	fo.write(hdr_bytes)
	fo.write(code_bytes)
	fo.write(text_bytes)
	fo.close()
	
if __name__ == '__main__':
	if len(sys.argv) < 3:
		print('Usage: bgi_insert.py <out_dir> <file(s)>')
		print("(<out_dir> will be created if it doesn't exist)")
		print('(only extension-less files amongst <file(s)> will be processed)')
		sys.exit(1)
	out_dir = sys.argv[1]
	if not os.access(out_dir, os.F_OK):
		os.mkdir(out_dir)
	for arg in sys.argv[2:]:
		for script in glob.glob(arg):
			base, ext = os.path.splitext(script)
			if not ext and os.path.isfile(script):
				print('Inserting %s...' % script)
				insert_script(out_dir, script, bgi_setup.ilang)
