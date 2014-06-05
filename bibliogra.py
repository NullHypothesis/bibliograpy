#!/usr/bin/env python
#
# Copyright 2014 Philipp Winter <phw@nymity.ch>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import cgi
import errno

import latexcodec
import pybtex.database.input.bibtex as bibtex

esc = cgi.escape

def create_directory(dir_name):
    """
    Create directory tree if it does not exist already.
    """

    # The following code snippet is taken from:
    # <http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python>

    try:
        os.makedirs(dir_name)
    except OSError as err:
        if (err.errno == errno.EEXIST) and os.path.isdir(dir_name):
            pass
        else:
            raise

def read_file(file_name):
    """
    Read and return all data from `file_name'.
    """

    try:
        with open(file_name, "r") as fd:
            return fd.read()
    except IOError:
        return ""

def write_file(file_name, data):
    """
    Write `data' to `file_name'.
    """

    try:
        with open(file_name, "w") as fd:
            fd.write(data.encode("utf8"))
    except IOError as err:
        print >> sys.stderr, "[+] Error writing file: %s" % err

def author_to_string(author):
    """
    Convert a `Person' object to string.
    """

    first = " ".join(author.first())
    middle = " ".join(author.middle())
    last = " ".join(author.last())

    return " ".join([name for name in [first, middle, last] if name])

def print_article(bib_entry):
    """
    Convert the given BibTeX article to HTML.
    """

    year = journal = ""

    if bib_entry.fields.has_key("year"):
        year = bib_entry.fields["year"]

    if bib_entry.fields.has_key("journal"):
        journal = bib_entry.fields["journal"]

    return "Article in: <span class=\"venue\">%s</span>, %s" % \
            (esc(journal), esc(year))

def print_inproceedings(bib_entry):
    """
    Convert the given BibTeX inproceedings to HTML.
    """

    booktitle = year = publisher = ""

    if bib_entry.fields.has_key("booktitle"):
        booktitle = bib_entry.fields["booktitle"]

    if bib_entry.fields.has_key("year"):
        year = bib_entry.fields["year"]

    if bib_entry.fields.has_key("publisher"):
        publisher = bib_entry.fields["publisher"]

    return "In Proc. of: <span class=\"venue\">%s</span>, %s, %s" % \
           (esc(booktitle), esc(year), esc(publisher))

def print_proceedings(bib_entry):
    """
    Convert the given BibTeX proceedings to HTML.
    """

    year = publisher = ""

    if bib_entry.fields.has_key("year"):
        year = bib_entry.fields["year"]

    if bib_entry.fields.has_key("publisher"):
        publisher = bib_entry.fields["publisher"]

    return "<span class=\"venue\">Proceedings</span>, %s, %s" % \
           (esc(publisher), esc(year))

def print_techreport(bib_entry):
    """
    Convert the given BibTeX techreport to HTML.
    """

    year = institution = ""

    if bib_entry.fields.has_key("year"):
        year = bib_entry.fields["year"]

    if bib_entry.fields.has_key("institution"):
        institution = bib_entry.fields["institution"]

    return "<span class=\"venue\">Technical Report</span>, %s, %s" % \
           (esc(year), esc(institution))

def print_inbook(bib_entry):
    """
    Convert the given BibTeX book chapter to HTML.
    """

    year = publisher = ""

    if bib_entry.fields.has_key("year"):
        year = bib_entry.fields["year"]

    if bib_entry.fields.has_key("publisher"):
        publisher = bib_entry.fields["publisher"]

    return "<span class=\"venue\">Book chapter</span>, %s, %s" % \
            (esc(publisher), esc(year))

def print_book(bib_entry):
    """
    Convert the given BibTeX book to HTML.
    """

    year = publisher = ""

    if bib_entry.fields.has_key("year"):
        year = bib_entry.fields["year"]

    if bib_entry.fields.has_key("publisher"):
        publisher = bib_entry.fields["publisher"]

    return "<span class=\"venue\">Book</span>, %s, %s" % \
            (esc(publisher), esc(year))

def print_phdthesis(bib_entry):
    """
    Convert the given BibTeX Ph.D. thesis to HTML.
    """

    school = year = ""

    if bib_entry.fields.has_key("school"):
        school = bib_entry.fields["school"]

    if bib_entry.fields.has_key("year"):
        year = bib_entry.fields["year"]

    return "Ph.D thesis: <span class=\"venue\">%s</span>, %s" % \
           (esc(school), esc(year))

def print_misc(bib_entry):
    """
    Convert the given BibTeX stuff to HTML.
    """

    return "<span class=\"venue\">Miscellaneous</span>"

conversion_table = {
    "article": print_article,
    "techreport": print_techreport,
    "inproceedings": print_inproceedings,
    "proceedings": print_proceedings,
    "inbook": print_inbook,
    "book": print_book,
    "phdthesis": print_phdthesis,
    "misc": print_misc,
}

def format_authors(persons, hilight):
    """
    Generate an HTML-formatted list of authors or editors.
    """

    authors_list = []

    if persons.has_key("author"):
        author_type = "author"
    elif persons.has_key("editor"):
        author_type = "editor"
    else:
        raise IndexError("BibTeX entry has neither `author' nor "
                         "`editor' field.")

    for person in persons[author_type]:
        authors_list.append(" ".join(person.first() + \
                                    person.middle() + \
                                    person.last()))

    authors_str = "%s%s<br/>" % (", ".join(authors_list),
                                 " (editors)" if author_type == "editor" \
                                              else "")

    if hilight:
        authors_str = authors_str.replace(hilight, "<b>%s</b>" % hilight)

    return authors_str

def format_html(key, bib_entry, hilight = None):
    """
    Convert the given BibTeX entry to HTML.
    """

    html = []

    html.append("<li>")

    # Header including paper title and links to pdf and bibtex.

    html.append("<span class=\"paper\"><a href=\"#%s\">%s</a></span> " % \
                (key, esc(bib_entry.fields["title"])))

    html.append("<a name=\"%s\">[" % key)
    if bib_entry.fields.has_key("url"):
        html.append("</a><a href=\"%s\">pdf</a>, " % \
                    esc(bib_entry.fields["url"]))

    if os.path.isfile(sys.argv[1] + "/" + key + ".pdf"):
        html.append("<a href=\"pdf/%s.pdf\">cached pdf</a>, " % key)

    html.append("<a href=\"bibtex/%s.bib\">bib</a>]<br/>\n" % key)

    # Add author/editor list.

    try:
        html.append(format_authors(bib_entry.persons, hilight))
    except IndexError as err:
        print >> sys.stderr, "[+] %s" % err

    # Add venue/publication type.

    if not conversion_table.has_key(bib_entry.type):
        raise NotImplementedError("BibTeX type `%s' not supported.  "
                                  "Skipping" % bib_entry.type)

    venue = (conversion_table[bib_entry.type])(bib_entry)

    if hilight:
        venue = venue.replace(hilight, "<b>%s</b>" % hilight)

    html.append(venue)
    html.append("</li>")

    # Remove curly braces because latexcodec won't do it for us.

    final_html = "".join(html).replace("{", "").replace("}", "")

    return final_html.decode("latex")

def sort_by_year(bibdata, sort_reverse = False):
    """
    Convert BibTeX data to HTML code sorted by (reverse) year.
    """

    html = []

    html.append("<ul>\n")
    year = None

    def get_year(key):
        try:
            return bibdata.entries[key].fields["year"]
        except KeyError:
            return 0

    for bibkey in sorted(bibdata.entries.keys(),
                         key = lambda k: get_year(k),
                         reverse = sort_reverse):

        if not year:
            year = get_year(bibkey)

        current_year = get_year(bibkey)
        if current_year != year:
            html.append("</ul>\n<ul>\n")
            year = current_year

        try:
            html.append(format_html(bibkey,
                                    bibdata.entries[bibkey],
                                    hilight=str(year)))
        except NotImplementedError as err:
            print >> sys.stderr, "[+] %s" % err
            continue

    html.append("</ul>\n")

    return "".join(html)

def sort_by_author(bibdata, sort_reverse = False):
    """
    Convert BibTeX data to HTML code sorted by (reverse) author.
    """

    publications = {}
    html = []

    # Populate the dictionary `publications' whose keys are author names and
    # whose values are publications of the respective author.

    for bibkey in bibdata.entries:

        if len(bibdata.entries[bibkey].persons.values()) == 0:
            continue

        for author in bibdata.entries[bibkey].persons.values()[0]:

            if publications.has_key(author_to_string(author)):
                publications[author_to_string(author)].append(bibkey)
            else:
                publications[author_to_string(author)] = [bibkey]

    html.append("<ul>\n")
    author = None

    for author in sorted(publications.keys(),
                         key = lambda name: name.split(' ')[-1],
                         reverse = sort_reverse):

        try:
            for bibkey in publications[author]:
                html.append(format_html(bibkey,
                                        bibdata.entries[bibkey],
                                        hilight=author))
        except NotImplementedError as err:
            print >> sys.stderr, "[+] %s" % err
            continue

        html.append("</ul>\n<ul>\n")

    html.pop(-1)
    html.append("</ul>\n")

    return "".join(html)

def main():
    """
    Entry point for this tool.
    """

    if len(sys.argv) < 2:
        print >> sys.stderr, \
              "\nUsage: %s OUTPUT_DIR [BIBTEX_FILE]\n" % sys.argv[0]
        return 1

    create_directory(sys.argv[1])

    # Read a BibTeX file (if given) or otherwise read from stdin.

    parser = bibtex.Parser()
    if (len(sys.argv) == 3) and os.path.isfile(sys.argv[2]):
        bibdata = parser.parse_file(sys.argv[2])
    else:
        bibdata = parser.parse_stream(sys.stdin)

    header = read_file("header.tpl")
    footer = read_file("footer.tpl")

    # Write HTML files sorted by year and reverse year.

    write_file(sys.argv[1] + "/year.html",
               header + sort_by_year(bibdata) + footer)
    write_file(sys.argv[1] + "/year_reverse.html",
               header + sort_by_year(bibdata, sort_reverse = True) + footer)

    # Write HTML files sorted by author and reverse author.

    write_file(sys.argv[1] + "/author.html",
               header + sort_by_author(bibdata) + footer)
    write_file(sys.argv[1] + "/author_reverse.html",
               header + sort_by_author(bibdata, sort_reverse = True) + footer)

    return 0

if __name__ == "__main__":
    exit(main())
