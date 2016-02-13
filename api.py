from tornado import ioloop
from tornado import web
from tornado import options

from app.user import UserProcess, UserStatus

from lib import config


# Set basic options
options.define("port", default=6060, type=int, help="What port to run on")
options.define("debug", default=False, type=bool, help="Debug Mode")
options.define("config", default='dev',
               type=str, help="Section of config file to read")


if __name__ == "__main__":
    options.parse_command_line()
    port = options.options.port
    debug = options.options.debug
    config.read_config(options.options.config)
    CONFIG = config.CONFIG

    app = web.Application(
        [
            (r'/api/user/process', UserProcess),
            (r'/api/user/status', UserStatus),
        ],
        debug=debug,
        cookie_secret=CONFIG.get("cookie_secret"),
    )

    app.listen(port, protocol='https')
    print("Listening on port: " + str(port))
    ioloop.IOLoop.current().start()
