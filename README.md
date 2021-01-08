# ptxconf

Pen tablet and Touch screen Xinput Configuration tool (PTXConf). Configures
touch/pen devices to work with extended desktops and multiple screens on Linux.
Please find the installation and usage instructions in the documentation
located here:
[wenhsinjen.github.io/ptxconf/](http://wenhsinjen.github.io/ptxconf/)

This repo is a modified version for my own purposes. In particular, I don't
have a systray so I'm not guaranteeing any of that to work.

## Installation

Included in the ./install directory is:

1. A Dockerfile supporting installation for the gtk3 version on Debian Buster.
2. A Gentoo ebuild which can be added to your local overlay.
3. A docker-compose script which explains/automates the forwarding of your X server.

I run `xhost +local:docker && docker-compose run --rm ptxconf && xhost +local:docker`
to get the docker version running. I have done very little testing to check whether
the dependencies are necessary and sufficient to install (particularly on the ebuild).

Any testing or clarification requests are very welcome (please raise an issue).

## Contributors

* WenHsin Linda Jen 2015 ([original project](https://github.com/wenhsinjen/ptxconf))
* thelinuxdude 2020 ([upgrades to GTK3](https://github.com/thelinuxdude/ptxconf))
