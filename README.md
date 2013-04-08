# plonesource.org

The website [plonesource.org](http://plonesource.org/) lists checkout
information for Plone, Zope and add-on packages from github.

The [checkout information](http://plonesource.org/sources.cfg) comes in
a [mr.developer](https://pypi.python.org/pypi/mr.developer) compatible
format so that it can easily be used with buildout.



## Usage

Extend your buildout from the
[sources.cfg](http://plonesource.org/sources.cfg) and configure what
repositories you want to checkout with the `auto-checkout` option:

{{{ini
[buildout]
extends = http://plonesource.org/sources.cfg

auto-checkout =
    Products.CMFPlone
    zope.interface
    collective.transmogrifier
}}}



## Checkout a branch of a package

Checking out non-master branches is easy:

{{{ini
[buildout]
extends = http://plonesource.org/sources.cfg

auto-checkout =
    Products.CMFPlone

[branches]
Products.CMFPlone = 4.3.x
}}}


## URLs

Generated sources.cfg
    http://plonesource.org/sources.cfg

Last updated timestamp
    http://plonesource.org/last-update.txt
