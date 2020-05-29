import os
import re
import sys

class NotionConverter:
    def __init__(self):
        self.uuidPattern = re.compile(r'(.*) [a-z0-9]{32}')
        self.notionLinkPattern = re.compile(r'\[(.*)\]\(.*\.md\)')
    
    def stripUUID(self, name):
        match = self.uuidPattern.fullmatch(name)
        return None if match is None else match.group(1)
    
    def replaceMdLink(self, content):
        return re.subn(self.notionLinkPattern, lambda match : f'[[{match.group(1)}]]', content)

    def renameAll(self, path):
        self.mapping = {}
        for root, dirs, files in os.walk(path, topdown=True):
            dirs.clear()
            for filename in files:
                fullFilename = os.path.join(root, filename)
                if not fullFilename.endswith(".md"): continue

                title = None
                with open(fullFilename) as f:
                    title = f.readline()[2:-1].translate({ord("/") : None})
                    self.mapping[os.path.splitext(filename)[0].replace(" ", "%20")] = title
                    os.rename(fullFilename, os.path.join(root, title) + ".md")

                # Rename the directory associated with this md file
                dir = fullFilename[:-3]
                if os.path.isdir(dir):
                    os.rename(dir, os.path.join(root, title))
                    dirs.append(title)
        
    def replaceLinks(self, path):
        numLinks = 0
        for root, dirs, files in os.walk(path):
            for filename in files:
                fullFilename = os.path.join(root, filename)
                if not fullFilename.endswith(".md"): continue
                with open(fullFilename) as f:
                    content = f.read()
                    (content, n) = self.replaceMdLink(content)
                    numLinks += n
                with open(fullFilename, "w") as f:
                    f.write(content)
        return numLinks
    
    def doTask(self, path):
        self.renameAll(path)
        numLinks = self.replaceLinks(path)
        print(f'Fixed {numLinks} links')

if __name__ == "__main__":
    convert = NotionConverter()
    path = sys.argv[1] if len(sys.argv) > 1 else "Notion"
    convert.doTask(path)
