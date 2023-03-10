import json
from core.model.execution import Execution, SuccessIndicator
from dacite import from_dict
from pathlib import Path
from core.utils.log import Log


class BaseModule:
    """
    Base class for all modules
    """

    def __init__(self, execution_id: str, debug: bool):
        """
        Name: Module Name
        Description: Module Description
        OS : Windows, Linux, Mac, Android, iOS
        Platform: Powershell, Python
        Elevation Requirement: True, False
        Execution Timeout: N minutes
        Tactics: ID of MITRE ATT&CK Tactics
        Technique: ID of MITRE ATT&CK Technique
        """
        log_level = 'DEBUG' if debug else 'INFO'
        self.logger = Log(log_name='module', log_level=log_level).get_logger()
        self.execution_id = execution_id
        execution_dict = self.get_execution(execution_id)
        # Deserialize execution json into Execution object
        self.execution = from_dict(data_class=Execution, data=execution_dict)
        # Replace variable name in powershell script to actual value
        self.input_arguments = self.get_input_arguments()

    @staticmethod
    def get_execution(execution_id: str) -> dict:
        """
        Get Execution dict from executions json file by id
        """
        execution_file = Path(__file__).parent.parent / 'assets/executions.json'
        with open(execution_file, 'r', encoding='utf-8') as f:
            execution_data = json.load(f)
        return next(
            (e for e in execution_data['data'] if e['_id'] == execution_id), None
        )

    def get_enabled_success_indicator(self) -> SuccessIndicator:
        """
        Get the enabled success indicator
        """
        for indicator in self.execution.successIndicators:
            if indicator.enabled:
                return indicator

    def get_input_arguments(self) -> dict:
        """
        Turn input arguments into a dict
        """
        return {arg.name: arg.default[0] for arg in self.execution.inputArguments}

    def check_dependency(self) -> bool:
        """
        Check if dependencies are installed
        """

    def resolve_variable(self, command: str, input_arguments: dict = None) -> str:
        """
        Transfer ruby string format variable name to value
        Replace input arguments in command -> #{test} -> test_value
        """
        input_arguments = input_arguments or self.input_arguments
        for name, value in input_arguments.items():
            command = command.replace(f'#{{{name}}}', value)
        return command

    def execute(self):
        """
        Main execution function
        """
        self.logger.info('***\nExecution Phrase\n***')

    def success_indicate(self) -> bool:
        """
        Check if the output indicates success
        """
        pass

    def cleanup(self):
        """
        Clean up after the scenario
        """
        pass

    def output_parser(self, output: str) -> str:
        """
        Parse output result
        """
        pass

    def run(self):
        """
        Run the module
        """
        module_info = f"""
        Name: {self.execution.name}
        Description: {self.execution.description}
        OS : {", ".join(self.execution.os)}
        Platform: {", ".join(self.execution.supportedPlatforms)}
        Elevation Requirement: {self.execution.executor.elevationRequired}
        Execution Timeout: {self.execution.timeout} minutes
        Tactics: {", ".join([t['name'] for t in self.execution.tactics])}
        Technique: {", ".join([t['name'] for t in self.execution.techniques])}
        """
        self.logger.info(f"Running module:\n---\n {module_info}\n---\n")
        if self.check_dependency():
            self.logger.success('All dependency checks passed')
            self.execute()
            if self.success_indicate():
                self.logger.success('Module executed successfully')
            else:
                self.logger.error('Module executed unsuccessfully')
        else:
            self.logger.error('Module dependency check failed')
        self.cleanup()
