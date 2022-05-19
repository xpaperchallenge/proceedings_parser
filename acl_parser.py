"""
acl_parser
parse ACL anthology html

MIT License
2022 (c) Ryota SUZUKI, xpaper.challenge
"""

import sys,re,io
import bs4
from bs4 import BeautifulSoup
from typing import List,Tuple
# import pyperclip


class ACLPaper:
    def __init__(self, proc:str, title:str, authors:Tuple[str], pdf_url:str) -> None:
        self.proc: str = proc
        self.title: str = title
        self.pdf_url: str = pdf_url
        self.authors: Tuple[str] = authors

def acl_parse(fn: str) -> List[ACLPaper]:
    """
    acl_parse
    parse acl anthology html
    return list of ALCPaper, that has proc title, paper title, url of pdf, and tuple of authors

    fn : filename of html
    """

    with open(fn,"r",encoding="utf8") as fp:
        soup = BeautifulSoup(fp,'html.parser')

    tdiv_contents : bs4.Tag = soup.select_one("#main > div.card.bg-light.mb-2.mb-lg-4 > div")
    tli_contents : List[bs4.Tag] = list(tdiv_contents.select("li"))

    procs : List[Tuple[str,str]] = []

    for tl in tli_contents:
        ta : bs4.Tag = tl.find("a")
        proc_id : str = ta.attrs["href"]
        proc_name : str = ta.text
        procs.append((proc_id, proc_name))

    papers : List[ACLPaper]=[]

    for proc in procs:
        td : bs4.Tag = soup.select_one("div"+proc[0])
        ps : List[bs4.Tag] = td.findChildren("p",recursive=False)
        
        for p in ps:
            _ps : bs4.Tag = p.findChildren("span",recursive=False)
            
            s1 : bs4.Tag = _ps[0]
            s2 : bs4.Tag = _ps[1]

            ####### s1
            _as = s1.select("a")
            links=["",""]
            for _a in _as:
                t = re.sub("(^\\s+|\\s+$)","", _a.text)
                if t=="pdf":
                    links[0] = _a.attrs["href"]
                elif t=="bib":
                    None
                elif t=="abs":
                    links[1] = _a.attrs["href"]

            ###### s2
            t_title : bs4.Tag = s2.findChild("strong",recursive=False)
            title : str = t_title.text
            authors : List[str] = []
            a_authors : List[bs4.Tag] = t_title.find_next_siblings("a")
            for a_a in a_authors:
                authors.append(a_a.text)

            papers.append(ACLPaper(proc[1], title, tuple(authors), links[0]))

    return papers


if __name__=="__main__":
    if len(sys.argv)<=1:
        sys.stderr.write("acl_parser - Parse acl anthology html and output as TSV.\n\n")
        sys.stderr.write("[Usage]\n $ python acl_parser.py inputfile.html [outputfile.txt]\n")
        sys.exit(-1)
    
    papers = acl_parse(sys.argv[1])

    ofn:str = ""
    if len(sys.argv)<=3:
        ofn = sys.argv[2]
    else:
        ofn = sys.argv[1]+".txt"

    sout = io.StringIO()
    for p in papers:
        if p.proc==p.title:
            continue
        sout.write("\t".join([p.proc, p.title, p.pdf_url, ', '.join(p.authors)])+"\n")
    
    # pyperclip.copy(sout.getvalue())
    with open(ofn, "w", encoding="utf8") as fp:
        fp.write(sout.getvalue())

    sout.close()
