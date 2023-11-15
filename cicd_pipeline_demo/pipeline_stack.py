from aws_cdk import Stack, SecretValue, StageProps
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as cpactions
from aws_cdk import aws_codebuild as codebuild
from constructs import Construct


class PipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Artifact
        source_output = codepipeline.Artifact("SourceOutput")
        unittest_build_output = codepipeline.Artifact("UnitestBuildOuput")
        cdk_build_output = codepipeline.Artifact("CDKBuildOuput")
        # dev_output = codepipeline.Artifact("DevOuput")

        # Code Build Unit Test
        unittest_codebuild_project = codebuild.PipelineProject(
            self,
            "UnittestCodebuildProject",
            project_name="UnittestCodebuildProject",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0
            ),
            build_spec=codebuild.BuildSpec.from_object(
                {
                    "version": "0.2",
                    "phases": {
                        "install": {
                            "commands": [
                                "pip install -r requirements-dev.txt",
                                "echo $CODE_COMMIT_ID",
                            ]
                        },
                        "build": {
                            "commands": [
                                "python -m pytest -s -v unittest/test_lambda_logic.py"
                            ]
                        },
                    },
                    "artifacts": {},
                },
            ),
        )

        # Code Build CDK template
        cdk_code_build = codebuild.PipelineProject(
            self,
            "CodeBuildCDK",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0
            ),
            build_spec=codebuild.BuildSpec.from_object(
                {
                    "version": "0.2",
                    "phases": {
                        "install": {
                            "commands": [
                                "npm install -g aws-cdk",
                                "npm install -g cdk-assets",
                                "pip install -r requirements.txt",
                            ]
                        },
                        "build": {"commands": ["cdk synth --no-lookups"]},
                        "post_build": {
                            "commands": [
                                "for FILE in cdk.out/*.assets.json; do cdk-assets -p $FILE publish; done"
                            ]
                        },
                    },
                    "artifacts": {
                        "base-directory": "cdk.out",
                        "files": ["*.template.json"],
                    },
                },
            ),
        )

        # Github connection action
        source_action = cpactions.GitHubSourceAction(
            action_name="Github",
            owner="duytran",
            repo="cicd-pipeline-demo",
            branch="main",
            output=source_output,
            oauth_token=SecretValue.secrets_manager("githubtoken"),
        )

        # Build action
        unittest_build_action = cpactions.CodeBuildAction(
            environment_variables={
                "CODE_COMMIT_ID": {"value": source_action.variables.commit_id}
            },
            action_name="DoUnitTest",
            project=unittest_codebuild_project,
            input=source_output,
            outputs=[unittest_build_output],
        )

        # CDK build action
        cdk_build_action = cpactions.CodeBuildAction(
            action_name="BuildCfnTemplate",
            project=cdk_code_build,
            input=source_output,
            outputs=[cdk_build_output],
        )

        # Code Deploy Dev
        deploy_dev = cpactions.CloudFormationCreateUpdateStackAction(
            action_name="DeployDevApplication",
            template_path=cdk_build_output.at_path("DevApplicationStack.template.json"),
            stack_name="DevApplicationStack",
            admin_permissions=True,
        )

        # Code Deploy Stag

        # pipeline
        pipeline = codepipeline.Pipeline(
            self,
            "CicdPipelineDemo",
            pipeline_name="CicdPipelineDemo",
            cross_account_keys=False,
            stages=[
                {"stageName": "Source", "actions": [source_action]},
                {"stageName": "UnitTest", "actions": [unittest_build_action]},
                {"stageName": "BuildTemplate", "actions": [cdk_build_action]},
                {"stageName": "DeployDev", "actions": [deploy_dev]},
            ],
        )
