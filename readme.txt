BGI script tools (dumper/inserter)
Requires Python 3.x
contact kingshriek on #tlwiki@irc.rizon.net for any questions, bug reports, etc.

These are some tools that can work with script files from the BGI/Ethornell (Buriko General Interpreter) engine.
The tools are merely a text dumper/inserter, not a full disassembler/assembler, so the original binary script files are needed for reinsertion.
Also, these tools work on script files only, not system code (._bp) files.

The tools work with the actual binary script files themselves, not the archive files (usually data#####.arc) they are packed into.
Use an general extraction tool such as crass or ExtractData beforehand to extract the script files .arc files.

Dumping the scripts is done via bgi_dump.py.
Syntax is bgi_dump.py <script_file(s)>.
In the above, <script_file(s)> are the extensionless, binary script files (not the .txt files dumps).
The inserter will ignore files that have an extension, so a * wildcard is sufficient to process every script in a directory.
Script files will be dumped into .txt files in the same directory as the originals.

The script dumps are split into three sections.
First are all the character names that occur in the script.
Second is the text/dialogue (this includes ruby and backlog text as well). 
Dialogue text is marked with the speaker tag when applicable.
Third is any other miscellaneous text (such as choices) that don't fall into the first two categories.
It is typical in this section to see a ton of file names. Just leave these alone.

All text lines are prefixed with an identifier (language + line #) in brackets. Do not modify this as it's needed for reinsertion.
Comments can be added to the dump files by using // (C++ style) at the beginning of the line.
Each text line is marked with a comment that identifes what kind of text it is. 

Inserting the scripts is done via bgi_insert.py.
Syntax is bgi_insert.py <output_directory> <script_file(s)>.
In the above, <script_file(s)> are the extensionless, binary script files (not the .txt files dumps).
For insertion to work, the .txt file dumps must be in the same directory as the original binary script files.
The inserter will ignore files that have an extension, so a * wildcard is sufficient to process every script in a directory.
It is advised to use a different output directory than where the original script files reside (don't want to overwrite them if something goes wrong).

The inserted files can be used with the game without repacking into a .arc file. 
Just copy them into the game installation directory (not into a subfolder of it).
If you want to pack them into an .arc file, there are tools that do this (such as arccreate in the bgitools package).

The tools can be configured by modifying the bgi_setup.py file.
This file is set up by default for Japanese-->English translation 
For other language translations, it will probably need to be modified (to change text encodings and such).

Technical note 1:
The tools properly handle the pointer aliasing issue that is inherent to BGI script files.
By pointer aliasing, I mean that any duplicate text lines all reference a single string in the script file.
The script dumper works by dumping from the text commands, not the string table itself, so duplicate text lines are separated out.
For translations purposes, this is beneficial since two identical Japanese lines will not necessarily translate into two identical Japanese lines.
Also, the aliasing/duplication issue mentioned above is only handled in the text/dialogue (second section) of the dump files.
Therefore, each unique name/other text only needs to be translated once (doesn't make sense to separate out duplicates of these).

Technical note 2:
The tools currently handle two different versions of BGI scripts.
The different versions and logic to detect them resides in bgi_config.py.
These handle some differences such as existence of a header (or lack of) or text function formats.
Most of the important information to work the scripts is detailed here, so the tools should be fairly modular w/ respect to adding new formats.
