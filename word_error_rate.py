"""
@author Kiettiphong Manovisut

References:
https://en.wikipedia.org/wiki/Word_error_rate
https://www.github.com/mission-peace/interview/wiki

"""
import string
import numpy

class WER:
    def __init__(self, human_transcript=None, system_transcript=None, wer_html=None):
        self.human_transcript = human_transcript
        self.system_transcript = system_transcript
        self.r = self.text_format(filename=self.human_transcript) # baseline reference
        self.h = self.text_format(filename=self.system_transcript) # hypothesis, system generated
        self.wer_html = wer_html

    def text_format(self, filename=None):
        """Method to take in two file paths, and break into lists"""
        with open(filename, 'r', encoding='utf-8') as f:
            a = f.readlines()
        # Take out punctuation
        text_string = a[0]
        converted = text_string.translate(str.maketrans('', '', string.punctuation))
        # Convert to lowercase
        converted = converted.lower()
        # Convert to split
        stripped_values = converted.split(' ')
        return stripped_values

    def print_to_html(self, d):
        #filename = "diff.html"
        x = len(self.r)
        y = len(self.h)

        html = '<html><body><head><meta charset="utf-8"></head>' \
               '<style>.g{background-color:#0080004d}.r{background-color:#ff00004d}.y{background-color:#ffa50099}</style>'

        while True:
            if x == 0 or y == 0:
                break

            if self.r[x - 1] == self.h[y - 1]:
                x = x - 1
                y = y - 1
                html = '%s ' % self.h[y] + html
            elif d[x][y] == d[x - 1][y - 1] + 1:    # substitution
                x = x - 1
                y = y - 1
                html = '<span class="y">%s(%s)</span> ' % (self.h[y], self.r[x]) + html
            elif d[x][y] == d[x - 1][y] + 1:        # deletion
                x = x - 1
                html = '<span class="r">%s</span> ' % self.r[x] + html
            elif d[x][y] == d[x][y - 1] + 1:        # insertion
                y = y - 1
                html = '<span class="g">%s</span> ' % self.h[y] + html
            else:
                print('\nWe got an error.')
                break

        html += '</body></html>'

        with open(self.wer_html, 'w') as f:
            f.write(html)
        #f.close()
        print("Printed comparison to: {0}".format(self.wer_html))

    def get_word_error_rate(self):
        """Given two list of strings how many word error rate(insert, delete or substitution)."""
        d = numpy.zeros((len(self.r) + 1) * (len(self.h) + 1), dtype=numpy.uint16)
        d = d.reshape((len(self.r) + 1, len(self.h) + 1))
        for i in range(len(self.r) + 1):
            for j in range(len(self.h) + 1):
                if i == 0:
                    d[0][j] = j
                elif j == 0:
                    d[i][0] = i

        for i in range(1, len(self.r) + 1):
            for j in range(1, len(self.h) + 1):
                if self.r[i - 1] == self.h[j - 1]:
                    d[i][j] = d[i - 1][j - 1]
                else:
                    substitution = d[i - 1][j - 1] + 1
                    insertion = d[i][j - 1] + 1
                    deletion = d[i - 1][j] + 1
                    d[i][j] = min(substitution, insertion, deletion)
        result = float(d[len(self.r)][len(self.h)]) / len(self.r) * 100
        self.print_to_html(d)
        return result


if __name__ == "__main__":
    w = WER(human_transcript='./../data-feeds/human-transcripts/martha-human.txt',
            system_transcript='./../data-feeds/system-transcripts/martha.txt',
            wer_html='./../data-feeds/wer-outputs/martha.html')
    response = w.get_word_error_rate()
    print(f"Word error rate: {response:<6.6}%")#response)

# Sample of how the lists look before being compared for WER
#r = ['In', 'computational', 'linguistics', 'and', 'computer', 'science', ',', 'edit', 'distance', 'is', 'a', 'way', 'of', 'quantifying', 'how', 'dissimilar', 'two', 'strings', 'are', 'to', 'one', 'another', 'by', 'counting', 'the', 'minimum', 'number', 'of', 'operations', 'required', 'to', 'transform', 'one', 'string', 'into', 'the', 'other.', 'Edit', 'distances', 'find', 'applications', 'in', 'natural', 'language', 'processing,', 'where', 'automatic', 'spelling', 'correction', 'can', 'determine', 'candidate', 'corrections', 'for', 'a', 'misspelled', 'word', 'by', 'selecting', 'words', 'from', 'a', 'dictionary', 'that', 'have', 'a', 'low', 'distance', 'to', 'the', 'word', 'in', 'question']

#h = ['In', 'linguistics', 'and', 'computer', 'science', 'theory', ',', 'edit', 'distance', 'iss', 'a', 'way', 'of', 'quantifying', 'how', 'dissimilar', 'the', 'two', 'string', 'is', 'to', 'one', 'another', 'by', 'counting', 'the', 'number', 'of', 'operations', 'required', 'to', 'transform', 'one', 'string', 'into', 'the', 'other.', 'Edit', 'distances', 'find', 'applications', 'in', 'natural', 'language', 'processing,', 'where', 'automatic', 'spelling', 'correction', 'can', 'determine', 'candidate', 'corrections', 'for', 'a', 'misspelled', 'word', 'by', 'selecting', 'words', 'from', 'a', 'dictionary', 'that', 'have', 'a', 'low', 'distance', 'to', 'the', 'words', 'in', 'question']
