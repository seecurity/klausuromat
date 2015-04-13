# Externals
import logging
import os
import io
import json
import tempfile
import shutil

# Internals
import generator
import exceptions

# Helper (not needed in Python 3.3)
import __future_subprocess as subprocess


# Code generator that has the ability to verify it's own code
class CodeGenerator(generator.BasicGenerator):
    # Initialize
    def __init__(self, *args):
        # Let parent class do all the initializing stuff
        super().__init__(*args)

        # Save temp and log directory
        self._temp_dir = self._settings['TEMP_DIRECTORY']
        self._log_dir = self._settings['LOG_DIRECTORY']

        # Add environment path
        os.environ['PATH'] = self._settings['ENV_PATH']

    # Verify current operations
    def verify(self):
        # Retrieve code
        code = super().code(verify=True, comments=True)

        # Compile code
        code_path, executable_path = self._compile_code(code)

        # Verify
        self._verify_code(executable_path, code_path)

        # Delete temp files
        os.remove(executable_path)
        if os.path.isfile(code_path):
            os.remove(code_path)

    # Compile code and return a path to an executable
    def _compile_code(self, code):
        # Write code to temp file
        with tempfile.NamedTemporaryFile(suffix=self._language['extension'], dir=self._temp_dir, delete=False) as fd:
            fd.write(code.encode())
            code_path = fd.name

        # Executable file name
        executable_path = os.path.splitext(code_path)[0]

        # Try to compile
        try:
            command = self._language['verify']['compile'].format(code_path, executable_path)
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True,
                                    timeout=self._settings['COMPILE_TIMEOUT'])
        # Timeout: Log error
        except subprocess.TimeoutExpired as exc:
            logging.error('Compiling timed out: ' + exc.cmd)
            raise exceptions.GeneratorCompileError('Could not compile generated code in time') from exc
        # Compile error: Log error and save code for further analysis
        except subprocess.CalledProcessError as exc:
            logging.error('Compile error: ' + exc.cmd)
            self._save_compile_error(exc, code_path)
            raise exceptions.GeneratorCompileError('Could not compile generated code') from exc

        # Return path of created files
        return code_path, executable_path

    # Verify code by executing and retrieving a JSON object from it
    def _verify_code(self, executable_path, code_path):
        # Get output of executable
        try:
            output = subprocess.check_output(executable_path, universal_newlines=True,
                                             timeout=self._settings['EXECUTE_TIMEOUT'])
        # Timeout: Maybe there is an infinite loop somewhere?
        except subprocess.TimeoutExpired as exc:
            logging.error('Execution timed out: ' + exc.cmd)
            self._move_built_code(code_path)
            raise exceptions.GeneratorVerifyError('Execution of generated code timed out') from exc
        # Call error: Log error and save code for further analysis
        except subprocess.CalledProcessError as exc:
            logging.error('Code returned non-zero: ' + exc.cmd)
            self._move_built_code(code_path)
            raise exceptions.GeneratorVerifyError('Execution of compiled code returned non-zero') from exc

        # Build JSON object from output
        try:
            ids = json.loads(output)
        # Error on parsing: Probably broken verifying code pieces
        except ValueError as exc:
            logging.error('Error on parsing JSON object from executable "{}"'.format(os.path.basename(code_path)))
            self._move_built_code(code_path)
            raise exceptions.GeneratorVerifyError('Error on parsing JSON object from executable') from exc
        # Compare identifiers
        identical = self.compare_identifiers(ids)
        if not identical:
            logging.error('Predicted values of identifiers do not match real values '
                          'of identifiers in "{}"'.format(os.path.basename(code_path)))
            self._move_built_code(code_path)
            raise exceptions.GeneratorVerifyError('Identifiers not identical', operations=self._operations)

    # Private: Save error and move code to log directory
    def _save_compile_error(self, exc, code_path):
        # Save error
        with io.open('{}/{}.log'.format(self._log_dir, os.path.splitext(os.path.basename(code_path))[0]),
                     mode='w', encoding='utf-8') as fd:
            fd.write('\n'.join([exc.cmd, exc.output]))

        # Move code
        self._move_built_code(code_path)

    # Move code to log directory
    def _move_built_code(self, codePath):
        shutil.move(codePath, self._log_dir)
        logging.info('The code which caused the error above has been saved to the log directory')
