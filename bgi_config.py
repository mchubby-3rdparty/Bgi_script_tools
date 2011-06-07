# BGI version configurations
# These can possibly differ between different BGI games. Modify/add as necessary.

# no header
ver000 = {
'HDR_SIZE' : 0x0,    # base header size
'HDRAS_POS': None,   # offset of additional header data size (set to None if not used)

'STR_TYPE': 0x3,     # string type identifier
'FILE_TYPE': 0x7F,   # file type identifier

'TEXT_FCN': 0x140,   # function id for text command (set to None if not used)
'BKLG_FCN': 0x143,   # function id for backlog text command (set to None if not used)
'RUBY_FCN': 0x14B,   # function id for ruby command (set to None if not used)

'NAME_POS': 0x24,    # offset of TXT_FCN from name argument
'TEXT_POS': 0x2C,    # offset of TXT_FCN from text argument
'RUBYK_POS': 0x14,   # offset of RUBY_FCN from kanji argument
'RUBYF_POS': 0x0C,   # offset or RUBY_FCN from furigana argument
'BKLG_POS': 0x0C,    # offset of BKLG_FCN from text argument
}

# header beginning with "BurikoCompiledScriptVer1.00"
ver100 = {
'HDR_SIZE': 0x1C,    # base header size
'HDRAS_POS': 0x1C,   # offset of additional header data size (set to None if not used)

'STR_TYPE': 0x3,     # string type identifier
'FILE_TYPE': 0x7F,   # file type identifier

'TEXT_FCN': 0x140,   # function id for text command (set to None if not used)
'BKLG_FCN': 0x143,   # function id for backlog text command (set to None if not used)
'RUBY_FCN': 0x14B,   # function id for ruby command (set to None if not used)

'NAME_POS': 0x0C,    # offset of TXT_FCN from name argument
'TEXT_POS': 0x04,    # offset of TXT_FCN from text argument
'RUBYK_POS': 0x04,   # offset of RUBY_FCN from kanji argument
'RUBYF_POS': 0x0C,   # offset or RUBY_FCN from furigana argument
'BKLG_POS': 0x0C,    # offset of BKLG_FCN from text argument
}

# select which version based on known header string
def get_config(data):
	if data.startswith(b'BurikoCompiledScriptVer1.00\x00'):
		config = ver100
	else:
		config = ver000
	return config
