class BriefcaseError(Exception):
    def __init__(self, error_code, skip_logfile=False):
        self.error_code = error_code
        self.skip_logfile = skip_logfile


class BriefcaseWarning(Exception):
    def __init__(self, error_code, msg):
        self.error_code = error_code
        self.msg = msg

    def __str__(self):
        return self.msg


class HelpText(BriefcaseError):
    """Exceptions that contain help text and shouldn't be displayed as an error."""


class InputDisabled(BriefcaseError):
    def __init__(
        self,
        msg="Input is disabled; cannot request user input without a default",
    ):
        super().__init__(error_code=99)
        self.msg = msg

    def __str__(self):
        return self.msg


class NoCommandError(HelpText):
    def __init__(self, msg):
        super().__init__(error_code=-10, skip_logfile=True)
        self.msg = msg

    def __str__(self):
        return self.msg


class InvalidPlatformError(BriefcaseError):
    def __init__(self, requested, choices):
        super().__init__(error_code=-20, skip_logfile=True)
        self.requested = requested
        self.choices = choices

    def __str__(self):
        choices = ", ".join(sorted(self.choices, key=str.lower))
        return f"Invalid platform {self.requested!r}; (choose from: {choices})"


class InvalidFormatError(BriefcaseError):
    def __init__(self, requested, choices):
        super().__init__(error_code=-21, skip_logfile=True)
        self.requested = requested
        self.choices = choices

    def __str__(self):
        choices = ", ".join(sorted(self.choices, key=str.lower))
        return f"Invalid format {self.requested!r}; (choose from: {choices})"


class UnsupportedCommandError(BriefcaseError):
    def __init__(self, platform, output_format, command):
        super().__init__(error_code=-30, skip_logfile=True)
        self.platform = platform
        self.output_format = output_format
        self.command = command

    def __str__(self):
        return (
            f"The {self.command} command for the {self.platform} {self.output_format} format "
            "has not been implemented (yet!)."
        )


class BriefcaseConfigError(BriefcaseError):
    def __init__(self, msg):
        super().__init__(error_code=100, skip_logfile=True)
        self.msg = msg

    def __str__(self):
        return f"Briefcase configuration error: {self.msg}"


class UnsupportedHostError(BriefcaseError):
    def __init__(self, reason):
        super().__init__(error_code=110, skip_logfile=True)
        self.msg = reason

    def __str__(self):
        return self.msg


class BriefcaseCommandError(BriefcaseError):
    def __init__(self, msg, skip_logfile=False):
        super().__init__(error_code=200, skip_logfile=skip_logfile)
        self.msg = msg

    def __str__(self):
        return self.msg


class NetworkFailure(BriefcaseCommandError):
    DEFAULT_HINT = "is your computer offline?"

    def __init__(self, action, hint=None):
        self.action = action
        self.hint = hint if hint else self.DEFAULT_HINT
        super().__init__(msg=f"Unable to {action}; {self.hint}")


class MissingNetworkResourceError(BriefcaseCommandError):
    def __init__(self, url):
        self.url = url
        super().__init__(msg=f"Unable to download {url}; is the URL correct?")


class BadNetworkResourceError(BriefcaseCommandError):
    def __init__(self, url, status_code):
        self.url = url
        self.status_code = status_code
        super().__init__(msg=f"Unable to download {url} (status code {status_code})")


class MissingToolError(BriefcaseCommandError):
    def __init__(self, tool):
        self.tool = tool
        super().__init__(msg=f"Unable to locate {tool!r}. Has it been installed?")


class IncompatibleToolError(BriefcaseCommandError):
    def __init__(self, tool: str, env_var: str):
        self.tool = tool
        super().__init__(
            msg=f"""\
Briefcase cannot install {tool} on this machine.

Install {tool} manually and specify the installation directory in the {env_var} environment variable.
            """
        )


class NonManagedToolError(BriefcaseCommandError):
    def __init__(self, tool):
        self.tool = tool
        super().__init__(msg=f"{tool!r} is using an install that is user managed.")


class UpgradeToolError(BriefcaseCommandError):
    def __init__(self, error_msg):
        super().__init__(msg=error_msg, skip_logfile=True)


class InvalidTemplateBranch(BriefcaseCommandError):
    def __init__(self, template_repo, branch):
        self.template_repo = template_repo
        self.branch = branch
        super().__init__(
            f"Could not find a branch named {branch!r} in template repository {template_repo!r}."
        )


class InvalidTemplateRepository(BriefcaseCommandError):
    def __init__(self, template):
        self.template = template
        super().__init__(
            f"Unable to clone application template; is the template path {template!r} correct?"
        )


class UnsupportedPlatform(BriefcaseCommandError):
    def __init__(self, platform):
        self.platform = platform
        super().__init__(
            f"""\
App cannot be deployed on {platform}. This is probably because one or more
requirements (e.g., the GUI library) doesn't support {platform}.
"""
        )


class InvalidSupportPackage(BriefcaseCommandError):
    def __init__(self, filename):
        self.filename = filename
        super().__init__(f"Unable to unpack support package {str(filename)!r}.")


class InvalidStubBinary(BriefcaseCommandError):
    def __init__(self, filename):
        self.filename = filename
        super().__init__(f"Unable to unpack or copy stub binary {str(filename)!r}.")


class MissingAppMetadata(BriefcaseCommandError):
    def __init__(self, app_bundle_path):
        super().__init__(f"Unable to find {str(app_bundle_path / 'briefcase.toml')!r}")


class MissingSupportPackage(BriefcaseCommandError):
    def __init__(self, python_version_tag, platform, host_arch, is_32bit):
        self.python_version_tag = python_version_tag
        self.platform = platform
        self.host_arch = host_arch
        self.is_32bit = is_32bit
        platform_name = f"{'32 bit ' if is_32bit else ''}{platform}"
        super().__init__(
            f"""\
Unable to download {platform_name} support package for Python {self.python_version_tag} on {self.host_arch}.

This is likely because either Python {self.python_version_tag} and/or {self.host_arch} is not yet
supported on {platform_name}. You will need to:
    * Use an older version of Python; or
    * Compile your own custom support package.
"""
        )


class MissingStubBinary(BriefcaseCommandError):
    def __init__(self, python_version_tag, platform, host_arch, is_32bit):
        self.python_version_tag = python_version_tag
        self.platform = platform
        self.host_arch = host_arch
        self.is_32bit = is_32bit
        platform_name = f"{'32 bit ' if is_32bit else ''}{platform}"
        super().__init__(
            f"""\
Unable to download {platform_name} stub binary for Python {self.python_version_tag} on {self.host_arch}.

This is likely because either Python {self.python_version_tag} and/or {self.host_arch} is not yet
supported on {platform_name}. You will need to:
    * Use an older version of Python; or
    * Compile your own stub binary.
"""
        )


class RequirementsInstallError(BriefcaseCommandError):
    def __init__(self, install_hint=""):
        super().__init__(
            f"""\
Unable to install requirements. This may be because one of your
requirements is invalid, or because pip was unable to connect
to the PyPI server.{install_hint}
"""
        )


class UnsupportedPythonVersion(BriefcaseCommandError):
    def __init__(self, version_specifier, running_version):
        super().__init__(
            f"""\
Unable to run Briefcase command. The project configuration requires
Python versions {version_specifier}, but the environment's Python
version is {running_version}. Please run Briefcase using a Python
version that satisfies the project's requirements.
"""
        )


class MissingAppSources(BriefcaseCommandError):
    def __init__(self, src):
        self.src = src
        super().__init__(f"Application source {src!r} does not exist.")


class InvalidDeviceError(BriefcaseCommandError):
    def __init__(self, id_type, device):
        self.id_type = id_type
        self.device = device
        super().__init__(msg=f"Invalid device {id_type} {device!r}")


class CorruptToolError(BriefcaseCommandError):
    def __init__(self, tool):
        self.tool = tool
        super().__init__(msg=f"{tool!r} found, but it appears to be corrupted.")


class CommandOutputParseError(BriefcaseCommandError):
    def __init__(self, parse_error):
        super().__init__(msg=f"Unable to parse command output: {parse_error}")


class BriefcaseTestSuiteFailure(BriefcaseError):
    def __init__(self):
        super().__init__(error_code=1000, skip_logfile=True)


class NoDistributionArtefact(BriefcaseWarning):
    def __init__(self, msg):
        super().__init__(error_code=0, msg=msg)


class NotarizationInterrupted(BriefcaseWarning):
    def __init__(self, msg):
        super().__init__(error_code=0, msg=msg)


class ParseError(Exception):
    """Raised by parser functions to signal parsing was unsuccessful."""
