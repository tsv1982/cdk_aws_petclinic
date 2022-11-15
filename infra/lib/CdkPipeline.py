from aws_cdk import (
    Stack,
    pipelines,
    Stage,
)

from constructs import Construct

from infra.lib.networking_stack import NetworkingStack
from infra.lib.rds_stack import RdsStack
from infra.lib.tsv_ecs_stack import TsvEcsStack
from infra.lib.pipeline_stack import PipelineStack

DB_CREDS_ARN = "arn:aws:secretsmanager:eu-central-1:090146717911:secret:petclinic02-hf0IeK"


class CdkPipeline(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_output = pipelines.CodePipelineSource.connection("tsv1982/cdk_aws_petclinic", "main",
                                                                connection_arn="arn:aws:codestar-connections:eu-central-1:090146717911:connection/846fb039-cf68-47a4-b1f3-02d599d50af3"
                                                                )

        pipeline = pipelines.CodePipeline(self, "Pipeline",
                                          synth=pipelines.ShellStep("Synth",
                                                                    input=source_output,
                                                                    commands=["pip install -r ./infra/requirements.txt",
                                                                              "npm install -g aws-cdk",
                                                                              "cdk synth",
                                                                              "pip install install-jdk",
                                                                              "pip install maven"]
                                                                    ),
                                          self_mutation=True,
                                          )

        pipeline.add_stage(InfrastructureStage(self, "infra"))


class InfrastructureStage(Stage):
    def __init__(self, scope, id, *, env=None, outdir=None):
        super().__init__(scope, id, env=env, outdir=outdir)

        networking_stack = NetworkingStack(self, "Networking_petclinic")
        rds_stack = RdsStack(self, "RdsStack_petclinic", vpc=networking_stack.vpc, creds_arn=DB_CREDS_ARN)
        ecs_stack = TsvEcsStack(self, "TsvEcsStack_petclinic", vpc=networking_stack.vpc, db_secret=rds_stack.db_credentials)
        ecs_stack.add_dependency(rds_stack)
        PipelineStack(self, "PipelineStack_petclinic", service=ecs_stack.service)
