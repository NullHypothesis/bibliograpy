bibliograpy
===========

This tool converts BibTeX files to HTML bibliographies.

Dependencies
============

You need [`Pybtex`](http://pybtex.sourceforge.net/) and
[`latexcodec`](https://github.com/mcmtroffaes/latexcodec).

Usage
=====

To create an HTML bibliography in `OUTPUT_DIRECTORY`, simply run:

    $ ./bibliograpy OUTPUT_DIRECTORY BIBTEX_FILE

Alternatively, you can feed the tool over `stdin`:

    $ cat BIBTEX_FILE | ./bibliograpy OUTPUT_DIRECTORY

Running `bibliograpy` will result in four HTML files which sort the
bibliography by year, reverse year, author, and reverse author.  Furthermore,
the tool tries to add links to local copies of publications.  It adds such a
link if it can find the respective publication in
`OUTPUT_DIRECTORY/pdf/BIBTEX_KEY.pdf`.  So if you have a BibTeX entry which
starts with `@inproceedings{JohnDoe, ...}`, then `bibliograpy` will look for
`OUTPUT_DIRECTORY/pdf/JohnDoe.pdf`.

Alternatives
============
Don't like `bibliograpy`?  Then have a look at
[`bibtex2html`](https://www.lri.fr/~filliatr/bibtex2html/),
[`bibhtml`](http://nxg.me.uk/dist/bibhtml/),
[`bib2xhtml`](http://www.spinellis.gr/sw/textproc/bib2xhtml/), or
[`anonbib`](https://gitweb.torproject.org/anonbib.git).

Feedback
========
Feel free to contact <phw@nymity.ch>.  You can use
[this](http://www.cs.kau.se/philwint/gpg/openpgp.html) OpenPGP key.
