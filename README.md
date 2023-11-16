
# Basic CI/CD Pipeline!

## Introduction

This shows a basic examle of a ci/cd pipeline for a lambda: codebuild for unittest, codeploy for deploy the lambda stack.

![AWS diagram](/img/diagram.png)

## Github Generate Auth Key Setting

![Github setting](/img/github.png)

## Push lambda asset after build cdk stack

```python
# Code Build CDK template
cdk_code_build_project = codebuild.PipelineProject(
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

# create permission to assume the file asset publishing role
assets_publishing_permissions = iam.PolicyStatement(
    sid="extraPermissionsRequiredForPublishingAssets",
    effect=iam.Effect.ALLOW,
    actions=["sts:AssumeRole"],
    resources=[
        f"arn:aws:iam::{Aws.ACCOUNT_ID}:role/cdk-{DefaultStackSynthesizer.DEFAULT_QUALIFIER}-file-publishing-role-{Aws.ACCOUNT_ID}-{Aws.REGION}"
    ],
)

# attach the permission to the role created with build cdk job
cdk_code_build_project.add_to_role_policy(assets_publishing_permissions)
```

## Reference

* [cicd-integration-test](https://github.com/cdk-entest/cicd-integration-test)
* [Webhook could not be registered with GitHub.](https://github.com/0x4447/0x4447_product_s3_email/issues/22)
* [CDK Deploy-Step Fails - Lambda Assets not uploaded to S3 after build ](https://github.com/aws/aws-cdk/issues/11025)
* [Github Source Action](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_codepipeline_actions/GitHubSourceAction.html)


## How to run

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
