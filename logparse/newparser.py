import os
import sys
import re
import json
import argparse
import time
import linecache
from datetime import timedelta

parser = argparse.ArgumentParser(description='Command line arguments')
parser.add_argument('-f', '--file', help='file name', required=True, type=str)
parser.add_argument('-t', '--type', help='date type, such as: testlog, tomcat, payara or octopus', required=True, type=str, nargs='+')  # more type can be added
parser.add_argument('-r', '--regex', help='regex to find in log message', type=str)
args = parser.parse_args()
the_true_last_line = ""

def write_to_json(word_count):
    open("lastline.json", "w").write(json.dumps(word_count))
    
def readlines_reverse(filename):
    with open(filename) as qfile:
        qfile.seek(0, os.SEEK_END)
        position = qfile.tell()
        line = ''
        while position >= 0:
            qfile.seek(position)
            next_char = qfile.read(1)
            if next_char == "\n":
                yield line[::-1]
                line = ''
            else:
                line += next_char
            position -= 1
        yield line[::-1]

def get_the_last_line(g):
    return the_true_last_line

def write_last_line_to_the_file(last_line):
    data = { args.file : last_line }
    write_to_json(data)
    return last_line
        
def try_to_read_last_data(g):
    # Check if file is empty.
    if os.path.getsize('lastline.json') > 0:
        # Check if the file was processed before.
        readedFromJson = json.loads(open('lastline.json', 'r').read())
        if not (readedFromJson.get(args.file) is None):          
            last_line = readedFromJson[args.file]
            print("The file was readed before up until: " + str(last_line))
            new_last_line = parsing_the_data_if_it_was_processed_before(last_line)           
            return new_last_line
        else:
            print("The file was not readed before!")
            print("Reading the file from the start!")
            last_line = parse_the_data(g)
            return last_line
    else:
        print("The file was not readed before!")
        print("Reading the file from the start!")
        last_line = parse_the_data(g)
        return last_line
 
def parse_the_data(g):
    building = False
    lastLineSave = ""
    f = open("output2.txt", "a")
    for i, line in enumerate(g):        
        
        anotherLineStr = line.rstrip('\n')
        
        if building == False:
            builderString = ""
        # Start building upon { symbol.
        if anotherLineStr.endswith('{') == True:
            building = True
                    
        if building == True:                                        
            builderString += anotherLineStr + str('\n')
                   
            if anotherLineStr.startswith('}') == True:
                building = False    
                anotherLineStr = builderString
                         
        if building == False:
            regex_pattern = re.compile(args.regex)
            x = re.findall(regex_pattern, anotherLineStr)
            if x:
                #anotherLineStr = anotherLineStr[26:]
                f.write(anotherLineStr)
                f.write("\n")
        # If line is too short it can't be a date.
        if len(anotherLineStr) > 30:
            lastLineSave = anotherLineStr
    return lastLineSave                                              
    f.close() 

def parsing_the_data_if_it_was_processed_before(last_line):
    f = open("output2.txt", "a")
    #Preparing the new nex line.
    next_last_line = last_line
    building = False
    is_set = False
    for qline in readlines_reverse(args.file):
        #If the line matches with the readed quit reading.
        if qline[0:30] == last_line[0:30]:
            break
        else:
            
            anotherLineStr = qline.replace('\n', '') 
            if building == False:
                builderString = ""
            
            # Turn on building if we find } symbol.
            if anotherLineStr.startswith('}') == True:
                building = True
            
            if building == True and anotherLineStr != '\n':                                        
                builderString = anotherLineStr + str('\n') + builderString
            # Turn off building if we find } symbol.
            if anotherLineStr.endswith('{') == True:
                building = False    
                anotherLineStr = builderString
        
            if building == False:
                 # Setting the new line to save as last.
                if is_set == False and len(anotherLineStr)>30:
                    next_last_line = anotherLineStr
                    is_set = True
                regex_pattern = re.compile(args.regex)
                x = re.findall(regex_pattern, anotherLineStr)
                if x:                    
                    # Searching for regex, print if it's a match.
                    #anotherLineStr = anotherLineStr[26:]
                    # Reversing the string.
                    anotherLineStr = "".join(filter(str.strip, anotherLineStr.splitlines(True)))
                    f.write(anotherLineStr)
                    f.write("\n")                    
                
    f.close()
    return next_last_line

if __name__ == "__main__":
    g = open(args.file, 'r', encoding='utf-8')
    new_last_line = try_to_read_last_data(g)
    new_last_line = new_last_line[0:35]
    write_last_line_to_the_file(new_last_line)
    g.close()
    