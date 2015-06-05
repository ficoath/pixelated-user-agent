#
# Copyright (c) 2015 ThoughtWorks, Inc.
#
# Pixelated is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pixelated is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.

import sys

from twisted.internet import reactor
from twisted.internet.threads import deferToThread
from twisted.internet import defer
from twisted.web.server import Site
from twisted.internet import ssl
from OpenSSL import SSL
from OpenSSL import crypto

from pixelated.config import arguments
from pixelated.resources import loading_page
from pixelated.config.initialize_leap import initialize_leap
from pixelated.config.register import register
from pixelated.config import logger, app_factory


@defer.inlineCallbacks
def start_user_agent(loading_app, host, port, sslkey, sslcert, leap_home, leap_session):
    yield loading_app.stopListening()

    resource = app_factory.init_app(leap_home, leap_session)

    if sslkey and sslcert:
        reactor.listenSSL(port, Site(resource), _ssl_options(sslkey, sslcert), interface=host)
    else:
        reactor.listenTCP(port, Site(resource), interface=host)

    # soledad needs lots of threads
    reactor.threadpool.adjustPoolsize(5, 15)


def _ssl_options(sslkey, sslcert):
    with open(sslkey) as keyfile:
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, keyfile.read())
    with open(sslcert) as certfile:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, certfile.read())

    acceptable = ssl.AcceptableCiphers.fromOpenSSLCipherString(
        u'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA:!RC4:HIGH:!MD5:!aNULL:!EDH')
    options = ssl.CertificateOptions(privateKey=pkey,
                                     certificate=cert,
                                     method=SSL.TLSv1_2_METHOD,
                                     acceptableCiphers=acceptable)
    return options


def initialize():
    args = arguments.parse_user_agent_args()
    logger.init(debug=args.debug)

    if args.register:
        register(*args.register)
        sys.exit(0)

    loading_app = reactor.listenTCP(args.port, Site(loading_page.LoadingResource()), interface=args.host)

    deferred = deferToThread(
        lambda: initialize_leap(
            args.leap_provider_cert,
            args.leap_provider_cert_fingerprint,
            args.credentials_file,
            args.organization_mode,
            args.leap_home))

    deferred.addCallback(
        lambda leap_session: start_user_agent(
            loading_app,
            args.host,
            args.port,
            args.sslkey,
            args.sslcert,
            args.leap_home,
            leap_session))

    def _quit_on_error(failure):
        failure.printTraceback()
        reactor.stop()

    deferred.addErrback(_quit_on_error)

    reactor.run()