#!/usr/bin/env python
#
# Copyright 2014-2017 Philipp Winter <phw@nymity.ch>
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
"""
Turn BibTeX files into HTML bibliographies.
"""

import os
import sys
import cgi
import errno
import argparse

import latexcodec
import pybtex.database.input.bibtex as bibtex


def latex_to_html(string):
    """
    Convert LaTeX-formatted to HTML-formatted strings.
    """

    # Note that cgi.escape() only takes care of the characters '&', '<', '>',
    # and, since we set the "quote" parameter, '"'.

    return cgi.escape(string.decode("latex"), quote=True)


def create_directory(dir_name):
    """
    Create directory tree if it does not exist already.
    """

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

    year = bib_entry.fields.get("year", "")
    journal = bib_entry.fields.get("journal", "")
    volume = bib_entry.fields.get("volume", "")
    number = bib_entry.fields.get("number", "")
    publisher = bib_entry.fields.get("publisher", "")

    return ("Article in: <span class=\"venue\">%s</span> %s.%s, %s, %s\n" %
            (latex_to_html(journal), volume, number, latex_to_html(year),
             publisher))


def print_inproceedings(bib_entry):
    """
    Convert the given BibTeX inproceedings to HTML.
    """

    booktitle = bib_entry.fields.get("booktitle", "")
    publisher = bib_entry.fields.get("publisher", "")
    year = bib_entry.fields.get("year", "")

    return ("In Proc. of: <span class=\"venue\">%s</span>, %s, %s\n" %
            (latex_to_html(booktitle), latex_to_html(year),
             latex_to_html(publisher)))


def print_proceedings(bib_entry):
    """
    Convert the given BibTeX proceedings to HTML.
    """

    publisher = bib_entry.fields.get("publisher", "")
    year = bib_entry.fields.get("year", "")

    return ("<span class=\"venue\">Proceedings</span>, %s, %s\n" %
            (latex_to_html(publisher), latex_to_html(year)))


def print_techreport(bib_entry):
    """
    Convert the given BibTeX techreport to HTML.
    """

    year = bib_entry.fields.get("year", "")
    institution = bib_entry.fields.get("institution", "")

    return ("<span class=\"venue\">Technical Report</span>, %s, %s\n" %
            (latex_to_html(year), latex_to_html(institution)))


def print_inbook(bib_entry):
    """
    Convert the given BibTeX book chapter to HTML.
    """

    year = bib_entry.fields.get("year", "")
    publisher = bib_entry.fields.get("publisher", "")

    return ("<span class=\"venue\">Book chapter</span>, %s, %s\n" %
            (latex_to_html(publisher), latex_to_html(year)))


def print_book(bib_entry):
    """
    Convert the given BibTeX book to HTML.
    """

    year = bib_entry.fields.get("year", "")
    publisher = bib_entry.fields.get("publisher", "")

    return ("<span class=\"venue\">Book</span>, %s, %s\n" %
            (latex_to_html(publisher), latex_to_html(year)))


def print_phdthesis(bib_entry):
    """
    Convert the given BibTeX Ph.D. thesis to HTML.
    """

    school = bib_entry.fields.get("school", "")
    year = bib_entry.fields.get("year", "")

    return ("Ph.D thesis: <span class=\"venue\">%s</span>, %s\n" %
            (latex_to_html(school), latex_to_html(year)))


def print_misc(bib_entry):
    """
    Convert the given BibTeX stuff to HTML.
    """

    year = bib_entry.fields.get("year", "")

    return ("<span class=\"venue\">Miscellaneous</span>, %s\n" %
            latex_to_html(year))


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

    if "author" in persons:
        author_type = "author"
    elif "editor" in persons:
        author_type = "editor"
    else:
        raise IndexError("BibTeX entry has neither `author' nor "
                         "`editor' field.")

    for person in persons[author_type]:
        authors_list.append(
            " ".join(person.first() + person.middle() + person.last()))

    authors_list = [authors.decode("latex") for authors in authors_list]

    authors_str = "%s%s<br/>" % (", ".join(authors_list), " (editors)"
                                 if author_type == "editor" else "")

    if hilight:
        authors_str = authors_str.replace(hilight, "<b>%s</b>" % hilight)

    return authors_str


def format_url(url):
    """
    Return an HTML fragment with a clickable link.
    """

    url_types = [".pdf", ".ps", ".html", ".txt"]
    for url_type in url_types:
        if url.endswith(url_type):
            return "</a><a href=\"%s\">%s</a>, " % (cgi.escape(url),
                                                    url_type[1:])

    return "</a><a href=\"%s\">%s</a>, " % (cgi.escape(url), "url")


def format_html(key, bib_entry, output_dir, hilight=None):
    """
    Convert the given BibTeX entry to HTML.
    """

    html = []

    html.append("<li>\n")

    # Header including paper title and links to pdf and bibtex.

    html.append("<span class=\"paper\"><a href=\"#%s\">%s</a></span>\n" %
                (key, latex_to_html(bib_entry.fields["title"])))

    html.append("<a name=\"%s\">[" % key)
    if "url" in bib_entry.fields:
        html.append(format_url(bib_entry.fields["url"]))

    if os.path.isfile(os.path.join(output_dir, "pdf", key + ".pdf")):
        html.append("<a href=\"pdf/%s.pdf\">cached pdf</a>, " % key)
    elif os.path.isfile(os.path.join(output_dir, "ps", key + ".ps")):
        html.append("<a href=\"ps/%s.ps\">cached ps</a>, " % key)

    html.append("<a href=\"bibtex.html#%s\">bib</a>]<br/>\n" % key)

    # Add author/editor list.

    try:
        html.append(format_authors(bib_entry.persons, hilight))
    except IndexError as err:
        print >> sys.stderr, "[+] %s" % err

    # Add venue/publication type.

    if bib_entry.type not in conversion_table:
        raise NotImplementedError("BibTeX type `%s' not supported.  "
                                  "Skipping" % bib_entry.type)

    venue = (conversion_table[bib_entry.type])(bib_entry)

    if hilight:
        venue = venue.replace(hilight, "<b>%s</b>" % hilight)

    html.append(venue)

    # Append notes if they exist
    if "note" in bib_entry.fields:
        html.append("<span class=\"note\">%s</span>\n" %
                    latex_to_html(bib_entry.fields["note"]))

    html.append("</li>\n")

    # Remove curly braces because latexcodec won't do it for us.

    final_html = "".join(html).replace("{", "").replace("}", "")

    return final_html


def sort_by_year(bibdata, output_dir, sort_reverse=False):
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

    def get_venue(key):
        try:
            return bibdata.entries[key].fields["booktitle"]
        except KeyError:
            return 0

    for bibkey in sorted(bibdata.entries.keys(),
                         key=lambda k: (get_year(k), get_venue(k)),
                         reverse=sort_reverse):

        if not year:
            year = get_year(bibkey)

        current_year = get_year(bibkey)
        if current_year != year:
            html.append("</ul>\n<ul>\n")
            year = current_year

        try:
            html.append(format_html(bibkey, bibdata.entries[bibkey],
                                    output_dir, hilight=str(year)))
        except NotImplementedError as err:
            print >> sys.stderr, "[+] %s" % err
            continue

    html.append("</ul>\n")

    return "".join(html)


def sort_by_author(bibdata, output_dir, sort_reverse=False):
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

            if author_to_string(author) in publications:
                publications[author_to_string(author)].append(bibkey)
            else:
                publications[author_to_string(author)] = [bibkey]

    html.append("<ul>\n")
    author = None

    for author in sorted(publications.keys(),
                         key=lambda name: name.split(' ')[-1],
                         reverse=sort_reverse):

        try:
            for bibkey in publications[author]:
                html.append(format_html(bibkey, bibdata.entries[bibkey],
                                        output_dir,
                                        hilight=author))
        except NotImplementedError as err:
            print >> sys.stderr, "[+] %s" % err
            continue

        html.append("</ul>\n<ul>\n")

    html.pop(-1)
    html.append("</ul>\n")

    return "".join(html)


def dump_bibtex_entry(entry):
    """
    Convert pybtex's Entry() object back to an HTML-formatted BibTeX string.
    """

    # Create the BibTeX entry header and the HTML links.

    text = []
    text.append("<pre>\n")
    text.append("<a name=\"%s\">@</a>%s{<a href=\"bibtex.html#%s\">%s</a>,\n" %
                (entry.key, entry.type, entry.key, entry.key))

    # Create the author list.

    authors = []
    if entry.persons.get("author"):
        for author in entry.persons.get("author"):
            authors.append("%s" % author_to_string(author))
    text.append("  author = {%s},\n" % " and ".join(authors))

    # Create all remaining fields and close the BibTeX entry.

    for key in entry.fields:
        text.append("  %s = {%s},\n" % (key, entry.fields[key]))

    text.append("}\n")
    text.append("</pre>")

    return "".join(text)


def parse_args():

    desc_text = "Generate an HTML bibliography from a BibTeX file."

    parser = argparse.ArgumentParser(description=desc_text)

    parser.add_argument("OUTPUT_DIR",
                        help="The directory to which all HTML-formatted "
                        "output files are written to.")

    parser.add_argument("-H", "--header",
                        type=str,
                        default="header.tpl",
                        help="HTML header prepended to the HTML files.")

    parser.add_argument("-F", "--footer",
                        type=str,
                        default="footer.tpl",
                        help="HTML footer appended to the HTML files.")

    parser.add_argument("-f", "--file-name",
                        type=str,
                        default=None,
                        help="The BibTeX file.  If no BibTeX file is given as "
                        "input, BibTeX entries are read from stdin.")

    return parser.parse_args()


def main(output_dir,
         file_name=None,
         header_file="header.tpl",
         footer_file="footer.tpl"):
    """
    Entry point for this tool.
    """

    create_directory(output_dir)

    # Read a BibTeX file (if given) or otherwise read from stdin.

    parser = bibtex.Parser()
    if file_name:
        bibdata = parser.parse_file(file_name)
    else:
        bibdata = parser.parse_stream(sys.stdin)

    header = read_file(header_file)
    footer = read_file(footer_file)

    # Write HTML files sorted by year and reverse year.

    write_file(os.path.join(output_dir, "year.html"),
               header + sort_by_year(bibdata, output_dir) + footer)
    write_file(os.path.join(output_dir, "year_reverse.html"),
               header + sort_by_year(bibdata, output_dir,
                                     sort_reverse=True) + footer)

    # Write HTML files sorted by author and reverse author.

    write_file(os.path.join(output_dir, "author.html"),
               header + sort_by_author(bibdata, output_dir) + footer)
    write_file(os.path.join(output_dir, "author_reverse.html"),
               header + sort_by_author(bibdata, output_dir,
                                       sort_reverse=True) + footer)

    # Create HTML-formatted BibTex file.

    data = ["""
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
    "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<title>BibTeX entries</title>
</head>
<body>
 """]

    for bibkey in bibdata.entries:
        data.append(dump_bibtex_entry(bibdata.entries[bibkey]))

    data.append("</body>\n</html>\n")

    write_file(os.path.join(output_dir, "bibtex.html"), "".join(data))

    return 0


if __name__ == "__main__":

    args = parse_args()
    sys.exit(main(args.OUTPUT_DIR, args.file_name, args.header, args.footer))
