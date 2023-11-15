from aws_cdk import Stack, Duration
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class ApplicationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, configs: dict, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        # lambda function
        environment = configs.get("environment")
        _lambda.Function(
            self,
            "Lambda",
            function_name=f"HelloPipeline{environment}",
            runtime=_lambda.Runtime.PYTHON_3_11,
            timeout=Duration.seconds(10),
            code=_lambda.Code.from_asset("lambda"),
            handler="index.handler",
        )
