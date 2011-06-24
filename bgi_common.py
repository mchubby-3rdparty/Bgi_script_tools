# Common routines for handling BGI scripts

import struct

import bgi_config
import bgi_setup

def escape(text):
	text = text.replace('\n', '\\n')
	return text
	
def unescape(text):
	text = text.replace('\\n', '\n')
	return text

def get_byte(data, offset):
	bytes = data[offset:offset+1]
	if len(bytes) < 1:
		return None
	return struct.unpack('B', bytes)[0]

def get_word(data, offset):
	bytes = data[offset:offset+2]
	if len(bytes) < 2:
		return None
	return struct.unpack('<H', bytes)[0]

def get_dword(data, offset):
	bytes = data[offset:offset+4]
	if len(bytes) < 4:
		return None
	return struct.unpack('<I', bytes)[0]

def get_section_boundary(data):
	pos = -1
	# This is somewhat of a kludge to get the beginning of the text section as it assumes that the
	# code section ends with the byte sequence: 1B 00 00 00 (this is probably a return or exit command).
	while 1:
		res = data.find(b'\x1B\x00\x00\x00', pos+1)
		if res == -1:
			break
		pos = res
	return pos + 4
	
def split_data(data):
	config = bgi_config.get_config(data)
	section_boundary = get_section_boundary(data)
	hdr_size = config['HDR_SIZE']
	if config['HDRAS_POS'] is not None:
		hdr_size += get_dword(data, config['HDRAS_POS'])
	hdr_bytes = data[:hdr_size]
	code_bytes = data[hdr_size:section_boundary]
	text_bytes = data[section_boundary:]
	return hdr_bytes, code_bytes, text_bytes, config

def get_text_section(text_bytes):
	strings = text_bytes.split(b'\x00')
	addrs = []
	pos = 0
	for string in strings:
		addrs.append(pos)
		pos += len(string) + 1
	texts = [x.decode(bgi_setup.senc) for x in strings]
	text_section = {}
	for addr,text in zip(addrs,texts):
		text_section[addr] = text
	return text_section
	
	type is config['STR_TYPE']
	
def check(code_bytes, pos, cfcn, cpos):
	return cfcn is not None and get_dword(code_bytes, pos+cpos) == cfcn
	
def get_code_section(code_bytes, text_section, config):
	pos = 4
	code_size = len(code_bytes)
	code_section = {}
	ids = {'N': 1, 'T': 1, 'Z': 1}
	names = {}
	others = {}
	while pos < code_size:
		type = get_dword(code_bytes, pos-4)
		dword = get_dword(code_bytes, pos)
		text_addr = dword - code_size
		# check if address is in text section and data type is string or file
		if text_addr in text_section:
			text = text_section[text_addr]
			if type == config['STR_TYPE']:
				if check(code_bytes, pos, config['TEXT_FCN'], config['NAME_POS']): # check if name (0140)
					marker = 'N'
					comment = 'NAME'
					if text not in names:
						names[text] = ids[marker]
						ids[marker] += 1
					id = names[text]
				elif check(code_bytes, pos, config['TEXT_FCN'], config['TEXT_POS']): # check if text (0140)
					marker = 'T'
					name_dword = get_dword(code_bytes, pos+config['TEXT_POS']-config['NAME_POS'])
					if name_dword != 0:
						try:
							name_addr = name_dword - code_size
							name = text_section[name_addr]
							comment = 'TEXT 【%s】' % name
						except KeyError:
							comment = 'TEXT'
					else:
						comment= 'TEXT'
					id = ids[marker]
					ids[marker] += 1
				elif check(code_bytes, pos, config['RUBY_FCN'], config['RUBYK_POS']): # check if ruby kanji (014b)
					marker = 'T'
					comment = 'TEXT RUBY KANJI'
					id = ids[marker]
					ids[marker] += 1
				elif check(code_bytes, pos, config['RUBY_FCN'], config['RUBYF_POS']): # check if ruby furigana (014b)
					marker = 'T'
					comment = 'TEXT RUBY FURIGANA'
					id = ids[marker]
					ids[marker] += 1
				elif check(code_bytes, pos, config['BKLG_FCN'], config['BKLG_POS']): # check if backlog text (0143)
					marker = 'T'
					comment = 'TEXT BACKLOG'
					id = ids[marker]
					ids[marker] += 1
				else:
					marker = 'Z'
					comment = 'OTHER'
					if text not in others:
						others[text] = ids[marker]
						ids[marker] += 1
					id = others[text]
				record = text, id, marker, comment
				code_section[pos] = record
			elif type == config['FILE_TYPE']:
				marker = 'Z'
				comment = 'OTHER'
				if text not in others:
					others[text] = ids[marker]
					ids[marker] += 1
				id = others[text]
				record = text, id, marker, comment
				code_section[pos] = record
		pos += 4
	return code_section
