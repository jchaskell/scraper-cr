#Takes a folder of .txt files of raw Congressional Record, plus tsv file name and returns that tsv file with columns for date, speaker, speech

import os, re, sys, codecs

class fixCR():
    # def __init__(self): #need to read to it a list of the congresses for which
    #     ugh = "test"
        # print os.getcwd()

    def clean_file(self, data):
data = re.sub(r'From the Congressional Record Online through the Government Publishing Office \[www\.gpo\.gov\]', '', data)
data = re.sub(r"[\[]{1,2}\', \<a href\=[\"\''][^\s]+[\"\'']\>Page S[0-9]+\</a\>, u[\"\''][\]]{1,2}", "", data)
data = re.sub(r"[\[]{1,2}\', \<a href\=[\"\''][^\s]+[\"\'']\>Pages S[0-9]+\-S[0-9]+\</a\>, u[\"\''][\]]{1,2}", "", data)
data = re.sub(r"\<a href\=[\"\''][^\s]+[\"\'']\>([^\<\>]+)\</a\>", r"\1", data)
data = re.sub(r'\[?\[[\"\'], Page S[0-9]+, u[\'\"]?\]\]?', '', data)
data = re.sub(r'([\'\"]\]|\[u\\?[\'\"])', '', data)
data = re.sub(r'\s{2,}', ' ', data)
data = re.sub(r'\(?[\'\"], ([SH]\. Res\. [0-9]+|[SH]\.J\. Res\. [0-9]+|[HS]\. Con\. Res\. [0-9]+|S\. [0-9]+|H\.R\. [0-9]+), u[\'\"]\)?', r'\1', data)
matches = r"(((Mr\.|Ms\.|Mrs\.) [A-Z][ec]?[A-Z-]+\.)|((Mr\.|Ms\.|Mrs\.) [A-Z][ec]?[A-Z-]+ of \w+( \w+)?\.)|(The PRESIDENT pro tempore\.?)|(The PRESIDING OFFICER\.?)|(The PRESIDENT\.)|(The VICE PRESIDENT\.?)|(The PRESIDING OFFICER \(.*\)\.?))"
data = re.sub(matches, "\\n\\n\\1", data)
data = re.sub(r'(______)', "\\n\\n\\1\\n\\n", data)
data = re.sub(r'(There\s+being\s+no\s+objection,\s+the\s+\w+\s+was\s+ordered\s+to\s+be\s+printed\s+in\s+the\s+Record,\s+as\s+follows:)', '\\1\\n\\n', data) #need to fix splitting mechanism here - doesn't seem to be working

data = re.sub(r'(\\n){2,}', '\n', data)
data = re.sub(r'\\n', ' ', data)
lines = data.splitlines()
        return(lines)
lines[1050:1100]

    def enter_file(self, lines, date):
        #get date from filename:

        matches2 = r"^\s*(((Mr\.|Ms\.|Mrs\.) [A-Z][ec]?[A-Z-]+\.)|((Mr\.|Ms\.|Mrs\.) [A-Z][ec]?[A-Z-]+ of \w+( \w+)?\.)|(The PRESIDENT pro tempore\.?)|(The PRESIDING OFFICER\.?)|(The PRESIDENT\.)|(The VICE PRESIDENT\.?)|(The PRESIDING OFFICER \(.*\)\.?))( .*)"

        all_speeches = []
        speaker = ""
        speech = ""
        title = ""
        for i,l in enumerate(lines):
            #Check if lthere is a line break - seem to come before title change
            if re.search(r'__', l):
                if speaker:
                    all_speeches.append(title + "\t " + speaker + "\t " + speech + "\t" + date)
                speaker = ""
                speech = ""
            if re.match(r'\s*\[.*\]', l) or re.match(r'^\s*$', l) or len(l) == 0:
                continue
            #If title, change title
            elif re.match(r"^[\WA-Z0-9]+$", l): #include puncuation
                if re.search(r"(NOT VOTING|NAYS|YEAS)\-\-[0-9]+", l):
                    continue
                else:
                    title = l
            else:
                # if not re.match(r'[^\w]', l[-1]):
                #     continue
                mat = re.findall(matches2, l)
                if mat:
                    if speaker:
                        all_speeches.append(title + "\t " + speaker + "\t " + speech+ "\t" + date)
                    speaker = ""
                    speech = ""
                    if mat[0][0] != speaker:
                        # print  mat[0][0]
                        if speaker:
                            all_speeches.append(title + "\t " + speaker + "\t " + speech+ "\t" + date)
                        speaker = mat[0][0]
                        speech = mat[0][0] + mat[0][11]
                        if re.search(r'There\s+being\s+no\s+objection,\s+the\s+\w+\s+was\s+ordered\s+to\s+be\s+printed\s+in\s+the\s+Record,\s+as\s+follows:', l):
                            all_speeches.append(title + "\t " + speaker + "\t " + speech+ "\t" + date)
                            speaker = ""
                            speech = ""
                else:
                    if not speaker:
                        continue
                    else:
                        speech += " " + l
        if speaker:
            all_speeches.append(title+ "\t " + speaker + '\t ' + speech+ "\t" + date)
        return(all_speeches)

    def save(self, file_to_save, new_file):
        to_save = '\n'.join(file_to_save)
        with open(new_file, 'w') as file:
            file.write(to_save)

    def process_all(self, folder, new_file):
        files = os.listdir(folder)
        os.chdir(folder)

        complete_data = []

        for file in files:
            with open(file,'r') as f:
                    text= f.read()
            date = re.sub("\.txt", "", file)
            cleaned = self.clean_file(text)
            tsv = self.enter_file(cleaned, date)
            complete_data.append(tsv)

        complete_data_fix = []
        for b in complete_data:
            for a in b:
                complete_data_fix.append(a)

        complete = ["title\tspeaker\tspeech\tdate"]
        for a in complete_data_fix:
            complete.append(a)
        print(type(complete[1]))
        self.save(complete, new_file)

def main(folder, new_file):
    """If running on a set of speeches already saved to files, go through the speeches in the directory and filter into senator files for each congress"""
    #figure out what the years are and correspond them to congresses
    #create new folder with one file per senator per congress
    #go through files and filter out==----

    #get files in folder
    fix = fixCR()
    fix.process_all(folder, new_file)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Too few arguments")
        sys.exit()
    else:
        main(sys.argv[1], sys.argv[2])



