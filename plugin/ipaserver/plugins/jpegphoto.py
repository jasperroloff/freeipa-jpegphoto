from ipaserver.plugins.user import user
from ipalib import Bytes, _

user.takes_params += (
    Bytes(
        'jpegphoto?',
        cli_name='avatar',
        label=_("Avatar"),
        doc=_("Base-64 encoded user picture (jpegphoto)"),
        maxlength=100 * 1024,  # max 100 kB
    ),
)
