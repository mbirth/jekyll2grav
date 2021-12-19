jekyll2grav converter
=====================

This is a tool to convert my Jekyll-based [GitHub Pages](https://pages.github.com) blog/wiki
to [GRAV](https://getgrav.org).


Usage
-----

Copy `config.yaml.example` to `config.yaml` and modify according to your needs. Note that
`jekyll_dir` has to point to your Jekyll base directory while `grav_dir` has to point to your
`grav/user/pages` directory.

If not done already, update the Python environment:

    pipenv install

Then run the script:

    pipenv run ./jekyll2grav.py


Why GRAV?
---------

While a static site generator like Jekyll or Hugo has its advantages, I wanted something "more
inviting" in terms of editor experience (read: a CMS). While there's Netlify + NetlifyCMS to get
a CMS for a static site generator, you'll still depend on the Netlify service. Also, I wanted
to get rid of Google CSE (fka. Site Search) and use some integrated search instead.

To keep at least some simplicity, I didn't want the CMS to use MySQL or PostgreSQL but either
SQLite or flat-files instead.

While I considered e.g. BoltCMS, OctoberCMS or even headless CMSes like ProcessWire,
GRAV caught my eye.

Since it's using simple Markdown files in a folder structure and the site can be deployed by
simply copying everything to a PHP-capable server without the need for any special configuration,
it was the perfect candiate for migrating my Jekyll site. And thus this converter was born.

