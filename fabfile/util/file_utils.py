from tempfile import mkstemp
from shutil import move
from os import remove, close

def replace_in_file(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(file_path)
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
    #close temp file
    new_file.close()
    close(fh)
    old_file.close()
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)

def append_line_to_file(path, line):

    if line in open(path).read():
        return

    with open(path, "a") as myfile:
        myfile.write("\n")
        myfile.write(line)