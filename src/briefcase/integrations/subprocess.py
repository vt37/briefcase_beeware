import shlex
import subprocess


class Subprocess:
    """
    A wrapper around subprocess that can be used as a logging point for
    commands that are executed.
    """
    def __init__(self, command):
        self.command = command
        self._subprocess = subprocess

    def prepare(self):
        """
        Perform any environment preparation required to execute processes.
        """
        # This is a no-op; the native subprocess environment is ready-to-use.
        pass

    def final_kwargs(self, **kwargs):
        """Convert subprocess keyword arguments into their final form.
        """
        # If `env` has been provided, inject a full copy of the local
        # environment, with the values in `env` overriding the local
        # environment.
        try:
            extra_env = kwargs.pop('env')
            kwargs['env'] = self.command.os.environ.copy()
            kwargs['env'].update(extra_env)
        except KeyError:
            # No explicit environment provided.
            pass

        # If `cwd` has been provided, ensure it is in string form.
        try:
            cwd = kwargs.pop('cwd')
            kwargs['cwd'] = str(cwd)
        except KeyError:
            pass

        return kwargs

    def run(self, args, **kwargs):
        """A wrapper for subprocess.run()

        The behavior of this method is identical to subprocess.run(),
        except for the `env` argument. If provided, the current system
        environment will be copied, and the contents of env overwritten
        into that environment.
        """
        # Invoke subprocess.run().
        # Pass through all arguments as-is.
        # All exceptions are propagated back to the caller.
        self._log_command(args)
        self._log_environment(kwargs)

        try:
            command_result = self._subprocess.run(
                [
                    str(arg) for arg in args
                ],
                **self.final_kwargs(**kwargs)
            )
        except subprocess.CalledProcessError as exc:
            self._log_return_code(exc.returncode)
            raise

        self._log_return_code(command_result.returncode)
        return command_result

    def check_output(self, args, **kwargs):
        """A wrapper for subprocess.check_output()

        The behavior of this method is identical to subprocess.check_output(),
        except for the `env` argument. If provided, the current system
        environment will be copied, and the contents of env overwritten
        into that environment.
        """
        self._log_command(args)
        self._log_environment(kwargs)

        try:
            cmd_output = self._subprocess.check_output(
                [
                    str(arg) for arg in args
                ],
                **self.final_kwargs(**kwargs)
            )
        except subprocess.CalledProcessError as exc:
            self._log_output(exc.output, exc.stderr)
            self._log_return_code(exc.returncode)
            raise

        self._log_output(cmd_output)
        self._log_return_code(0)
        return cmd_output

    def Popen(self, args, **kwargs):
        """A wrapper for subprocess.Popen()

        The behavior of this method is identical to subprocess.Popen(),
        except for the `env` argument. If provided, the current system
        environment will be copied, and the contents of env overwritten
        into that environment.
        """
        self._log_command(args)
        self._log_environment(kwargs)

        return self._subprocess.Popen(
            [
                str(arg) for arg in args
            ],
            **self.final_kwargs(**kwargs)
        )

    def _log_command(self, args):
        """
        Log the entire console command being executed.
        """
        self.command.logger.debug1()
        self.command.logger.debug1("Running Command:")
        self.command.logger.debug1("    {cmdline}".format(
            cmdline=' '.join(shlex.quote(str(arg)) for arg in args)
        ))

    def _log_environment(self, kwargs=None):
        """
        Log the state of environment variables prior to command execution.
        """
        # use merged environment if it exists, else current environment
        env = (kwargs or {}).get("env") or self.command.os.environ
        self.command.logger.debug3("Environment:")
        for env_var, value in env.items():
            self.command.logger.debug3("    {env_var}={value}".format(env_var=env_var, value=value))

    def _log_output(self, output, stderr=None):
        """
        Log the output of the executed command.
        """
        if output:
            self.command.logger.debug2("Command Output:")
            for line in str(output).splitlines():
                self.command.logger.debug2("    {line}".format(line=line))

        if stderr:
            self.command.logger.debug2("Command Error Output (stderr):")
            for line in str(stderr).splitlines():
                self.command.logger.debug2("    {line}".format(line=line))

    def _log_return_code(self, return_code):
        """
        Log the output value of the executed command.
        """
        self.command.logger.debug2("Return code: {return_code}".format(return_code=return_code))
