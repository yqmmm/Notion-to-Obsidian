import os
import re
import sys

class NotionConverter:
    def __init__(self):
        self.uuidPattern = re.compile(r'(.*) [a-z0-9]{32}\.')
        self.notionLinkPattern = re.compile(r'\[(.*)\]\(.*\.(md|csv)\)')
        self.notionCsvLinkPattern = re.compile(r'\[(.*)\]\(.*/(.*\.csv)\)')
        self.csvMapping = {}
    
    def stripUUID(self, name):
        return re.sub(self.uuidPattern, lambda match : f'{match.group(1)}.', name)
    
    def replaceMdLink(self, content):
        return re.subn(self.notionLinkPattern, lambda match : f'[[{match.group(1)}]]', content)
    
    def findCsvLink(self, content):
        matches = self.notionCsvLinkPattern.findall(content)
        for match in matches:
            self.csvMapping[match[1].replace("%20", " ")] = match[0]

    def renameAll(self, path):
        for root, dirs, files in os.walk(path, topdown=True):
            dirs.clear()
            for filename in files:
                fullname = os.path.join(root, filename)
                if not fullname.endswith(".md") and not fullname.endswith(".csv"):
                    continue

                # Use the markdown title as the new filename
                with open(fullname) as f:
                    lines = f.readlines()
                    for line in lines:
                        self.findCsvLink(line)
                    if fullname.endswith(".md"):
                        title = lines[0][2:-1].translate({ord("/") : None})
                        os.rename(fullname, os.path.join(root, title) + ".md")
                    else:
                        title = self.csvMapping[filename]
                        os.rename(fullname, os.path.join(root, title) + "csv")

                # Rename the directory associated with this md file
                dir = os.path.splitext(fullname)[0]
                if os.path.isdir(dir):
                    os.rename(dir, os.path.join(root, title))
                    dirs.append(title)
    
    def convertMd(self, path):
        with open(path) as f:
            content = f.read()
            (content, n) = self.replaceMdLink(content)
        with open(path, "w") as f:
            f.write(content)
    
    def convertCsv(self, fullFilename):
        pass # TODO: implement
        
    def convertAll(self, path):
        for root, dirs, files in os.walk(path):
            for filename in files:
                fullFilename = os.path.join(root, filename)
                if fullFilename.endswith(".md"):
                    self.convertMd(fullFilename)
                elif fullFilename.endswith(".csv"):
                    self.convertCsv(fullFilename)
    
    def doTask(self, path):
        self.renameAll(path)
        self.convertAll(path)

if __name__ == "__main__":
    convert = NotionConverter()
    path = sys.argv[1] if len(sys.argv) > 1 else "Notion"
    convert.doTask(path)
