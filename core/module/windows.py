"""
Windows module for execution
"""

from core.module.base import BaseModule
from core.utils.common import powershell, powershell_return_code


class WindowsModule(BaseModule):
    def __init__(self, execution_id: str, debug: bool = True):
        super().__init__(execution_id=execution_id, debug=debug)

    def check_dependency(self) -> bool:
        failed_dependency = []
        for dependency in self.execution.dependencies:
            self.logger.info(f'Checking : {dependency.description}')
            if dependency.dependencyExecutorName == 'powershell':
                # Get-Pre-req command: Download files...etc
                get_pre_req_cmd = self.resolve_variable(dependency.getPrereqCommand)
                result = powershell(get_pre_req_cmd)
                self.logger.debug(f'Get-Pre-req command result: {result}\n')

                # Get-Pre-req command: Download files...etc
                pre_req_cmd = self.resolve_variable(dependency.prereqCommand)
                is_dependency_installed = powershell_return_code(pre_req_cmd) == 0
                if not is_dependency_installed:
                    self.logger.error(f'Failed this check: {dependency.description}')
                    failed_dependency.append(dependency.description)
                else:
                    self.logger.success(f'Passed this check: {dependency.description}')
        return not failed_dependency

    @staticmethod
    def resolve_file_path(variable: str) -> str:
        """
        Resolve absolute path for the variable in powershell
        """
        return powershell(f'echo {variable}')[0].decode('big5').strip()

    def set_input_arguments_abs(self):
        """
        Set input_arguments's values to resolve absolute path for the variable in powershell
        """
        input_arguments = self.get_input_arguments()
        for name, value in input_arguments.items():
            if value.startswith('$env'):
                self.input_arguments[name] = self.resolve_file_path(value)

    def execute(self):
        if self.execution.executor.name == 'powershell':
            # Not resolving absolute path at init because the temp path might change if evaluated to other users
            self.set_input_arguments_abs()
            powershell_script = self.resolve_variable(self.execution.executor.command)
            self.logger.debug(f'Running Powershell Script: {powershell_script}\n')
            result_list = powershell(powershell_script)
            result = "\n".join([r.decode('big5') for r in result_list])
            self.logger.debug(f'Powershell script result: {result}\n')

    def success_indicate(self) -> bool:
        success_flag = False
        for success_indicator in self.execution.successIndicators:
            if success_indicator.successIndicatorExecutor == "powershell":
                powershell_script = self.resolve_variable(success_indicator.successIndicatorCommand)
                result = powershell_return_code(powershell_script)
                if result == 0:
                    self.logger.success(f'Success Indicator: {success_indicator.description}')
                    success_flag = True
                    break
                else:
                    self.logger.warning(f'Failed Success Indicator: {success_indicator.description}')
        return success_flag
