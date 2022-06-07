"""
cvf_parser
parse CVF html

MIT License
2022 (c) Ryota SUZUKI, xpaper.challenge
"""

import sys,io
import bs4
from bs4 import BeautifulSoup
from typing import List

url_root = "https://openaccess.thecvf.com"

class CVFPaper:
    def __init__(self, title:str, authors:List[str], abs_url:str, pdf_url:str) -> None:
        self.title:str = title
        self.pdf_url:str = pdf_url
        self.abs_url:str = abs_url
        self.authors:List[str] = authors


def cvf_parse(fn:str) -> List[CVFPaper]:
    with open(fn,"r",encoding="utf8") as fp:
        soup : bs4.Tag = BeautifulSoup(fp, "html.parser")

    dts : List[bs4.Tag] = list(soup.select("dt.ptitle"))

    papers : List[CVFPaper] = []

    for dt in dts:
        dd1 : bs4.Tag = dt.find_next_sibling("dd")
        dd2 : bs4.Tag = dd1.find_next_sibling("dd")

        dd1_as : List[bs4.Tag] = dd1.find_all("a")
        authors:List[str] = [a.text for a in dd1_as]

        dta : bs4.Tag = dt.find("a")
        title: str = dta.text

        dd2_as : List[bs4.Tag] = dd2.find_all("a", recursive=False)
        links = ["","",""]
        links[0] = url_root + dta.attrs["href"]
        for a in dd2_as:
            if a.text == "pdf":
                links[1] = url_root + a.attrs["href"]
            elif a.text == "supp":
                links[2] = url_root +  a.attrs["href"]

        papers.append(CVFPaper(title, authors, links[0], links[1]))

    return papers


if __name__ == "__main__":
    # import pyperclip
    if len(sys.argv) <= 1:
        sys.stderr.write("cvf_parser - parse cvf html\n")
        sys.stderr.write("[Usage] $ python cvf_parser.py inputfile.html [outputfile.txt]\n")
        sys.exit(-1)

    papers = cvf_parse(sys.argv[1])

    sout = io.StringIO()
    for p in papers:
        s = "\t".join([p.title, ', '.join(p.authors), p.abs_url, p.pdf_url]) + "\n"
        sout.write(s)

    ofn : str = ""
    if len(sys.argv) >= 3:
        ofn = sys.argv[2]
    else:
        ofn = sys.argv[1] + ".txt"

    # pyperclip.copy(sout.getvalue())
    with open(ofn,"w",encoding="utf8") as fp:
        fp.write(sout.getvalue())

    sout.close()