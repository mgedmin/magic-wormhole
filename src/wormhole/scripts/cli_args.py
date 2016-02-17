import argparse
from textwrap import dedent
from .. import public_relay
from .. import __version__
from . import cmd_send, cmd_receive
from ..servers import cmd_server, cmd_usage

parser = argparse.ArgumentParser(
    usage="wormhole SUBCOMMAND (subcommand-options)",
    description=dedent("""
    Create a Magic Wormhole and communicate through it. Wormholes are created
    by speaking the same magic CODE in two different places at the same time.
    Wormholes are secure against anyone who doesn't use the same code."""),
    )

parser.add_argument("--version", action="version",
                    version="magic-wormhole "+ __version__)
g = parser.add_argument_group("wormhole configuration options")
g.add_argument("--relay-url", default=public_relay.RENDEZVOUS_RELAY,
               metavar="URL", help="rendezvous relay to use", type=type(u""))
g.add_argument("--transit-helper", default=public_relay.TRANSIT_RELAY,
               metavar="tcp:HOST:PORT", help="transit relay to use",
               type=type(u""))
g.add_argument("-c", "--code-length", type=int, default=2,
               metavar="WORDS", help="length of code (in bytes/words)")
g.add_argument("-v", "--verify", action="store_true",
               help="display (and wait for acceptance of) verification string")
g.add_argument("--hide-progress", action="store_true",
               help="supress progress-bar display")
subparsers = parser.add_subparsers(title="subcommands",
                                   dest="subcommand")


# CLI: run-server
s = subparsers.add_parser("server", description="Start/stop a relay server")
sp = s.add_subparsers(title="subcommands", dest="subcommand")
sp_start = sp.add_parser("start", description="Start a relay server",
                         usage="wormhole server start [opts] [TWISTD-ARGS..]")
sp_start.add_argument("--rendezvous", default="tcp:3000", metavar="tcp:PORT",
                      help="endpoint specification for the rendezvous port")
sp_start.add_argument("--transit", default="tcp:3001", metavar="tcp:PORT",
                      help="endpoint specification for the transit-relay port")
sp_start.add_argument("--advertise-version", metavar="VERSION",
                      help="version to recommend to clients")
sp_start.add_argument("--blur-usage", default=None, type=int,
                      metavar="SECONDS",
                      help="round logged access times to improve privacy")
sp_start.add_argument("-n", "--no-daemon", action="store_true")
#sp_start.add_argument("twistd_args", nargs="*", default=None,
#                      metavar="[TWISTD-ARGS..]",
#                      help=dedent("""\
#                      Additional arguments to pass to twistd"""),
#                      )
sp_start.set_defaults(func=cmd_server.start_server)

sp_stop = sp.add_parser("stop", description="Stop the relay server",
                        usage="wormhole server stop")
sp_stop.set_defaults(func=cmd_server.stop_server)

sp_restart = sp.add_parser("restart", description="Restart the relay server",
                           usage="wormhole server restart")
sp_restart.add_argument("--rendezvous", default="tcp:3000", metavar="tcp:PORT",
                        help="endpoint specification for the rendezvous port")
sp_restart.add_argument("--transit", default="tcp:3001", metavar="tcp:PORT",
                        help="endpoint specification for the transit-relay port")
sp_restart.add_argument("--advertise-version", metavar="VERSION",
                        help="version to recommend to clients")
sp_restart.add_argument("--blur-usage", default=None, type=int,
                        metavar="SECONDS",
                        help="round logged access times to improve privacy")
sp_restart.add_argument("-n", "--no-daemon", action="store_true")
sp_restart.set_defaults(func=cmd_server.restart_server)

sp_show_usage = sp.add_parser("show-usage", description="Display usage data",
                              usage="wormhole server show-usage")
sp_show_usage.add_argument("-n", default=100, type=int,
                           help="show last N entries")
sp_show_usage.set_defaults(func=cmd_usage.show_usage)

sp_tail_usage = sp.add_parser("tail-usage", description="Follow latest usage",
                              usage="wormhole server tail-usage")
sp_tail_usage.set_defaults(func=cmd_usage.tail_usage)

# CLI: send
p = subparsers.add_parser("send",
                          description="Send text message, file, or directory",
                          usage="wormhole send [FILENAME|DIRNAME]")
p.add_argument("--text", metavar="MESSAGE",
               help="text message to send, instead of a file. Use '-' to read from stdin.")
p.add_argument("--code", metavar="CODE", help="human-generated code phrase",
               type=type(u""))
p.add_argument("-0", dest="zeromode", action="store_true",
               help="enable no-code anything-goes mode")
p.add_argument("what", nargs="?", default=None, metavar="[FILENAME|DIRNAME]",
               help="the file/directory to send")
p.set_defaults(func=cmd_send.send)

# CLI: receive
p = subparsers.add_parser("receive",
                          description="Receive a text message, file, or directory",
                          usage="wormhole receive [CODE]")
p.add_argument("-0", dest="zeromode", action="store_true",
               help="enable no-code anything-goes mode")
p.add_argument("-t", "--only-text", dest="only_text", action="store_true",
               help="refuse file transfers, only accept text transfers")
p.add_argument("--accept-file", dest="accept_file", action="store_true",
               help="accept file transfer with asking for confirmation")
p.add_argument("-o", "--output-file", default=None, metavar="FILENAME|DIRNAME",
               help=dedent("""\
               The file or directory to create, overriding the name suggested
               by the sender."""),
               )
p.add_argument("code", nargs="?", default=None, metavar="[CODE]",
               help=dedent("""\
               The magic-wormhole code, from the sender. If omitted, the
               program will ask for it, using tab-completion."""),
               type=type(u""),
               )
p.set_defaults(func=cmd_receive.receive)