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


    [buildout]
    extends = http://plonesource.org/sources.cfg

    extensions =
        mr.developer

    auto-checkout =
        Products.CMFPlone
        zope.interface
        collective.transmogrifier




## Checkout a branch of a package

Checking out non-master branches is easy:


    [buildout]
    extends = http://plonesource.org/sources.cfg

    extensions =
        mr.developer

    auto-checkout =
        Products.CMFPlone

    [branches]
    Products.CMFPlone = 4.3.x


## Handling of forks

Forks are not include but the original repositories are.
The original repository is included even when the principal is not
configured in the
[config.ini](https://github.com/jone/plonesource.org/blob/master/config.ini).



## URLs

Generated sources.cfg
    http://plonesource.org/sources.cfg

Last updated timestamp
    http://plonesource.org/last-update.txt
