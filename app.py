#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cicd_pipeline_demo.pipeline_stack import PipelineStack
from cicd_pipeline_demo.application_stack import ApplicationStack

app = cdk.App()

PipelineStack(
    app,
    "CicdPipelineStack",
)

ApplicationStack(app, "DevApplicationStack", dict(environment="dev"))

app.synth()
