EAPI=7

DESCRIPTION="GTK3 front end for xinput map-to-output."
HOMEPAGE="https://github.com/danielittlewood0/ptxconf"
SRC_URI="https://github.com/danielittlewood0/ptxconf/archive/master.zip"

LICENSE="AGPL-3"
SLOT="0"
KEYWORDS="~amd64 ~x86"

DEPEND=""
RDEPEND="
	>=dev-lang/python-3.0
	x11-apps/xinput
	dev-python/pygobject
	dev-libs/libappindicator
	${DEPEND}
"
BDEPEND=""
