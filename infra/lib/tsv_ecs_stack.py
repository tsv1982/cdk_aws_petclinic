from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_secretsmanager as secrets,
    aws_ecs_patterns as ecs_patterns,
)

from constructs import Construct


class TsvEcsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, db_secret: secrets.Secret, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cluster = ecs.Cluster(self, "tsv_cluster_petclinic", cluster_name="tsv_cluster_petclinic", vpc=vpc)

        execution_role = iam.Role(self, "tsv_execution_role_petclinic",
                                  assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
                                  role_name="tsv_execution_role_petclinic")
        execution_role.add_to_policy(iam.PolicyStatement(effect=iam.Effect.ALLOW, resources=["*"],
                                                         actions=["ecr:GetAuthorizationToken",
                                                                  "ecr:BatchCheckLayerAvailability",
                                                                  "ecr:GetDownloadUrlForLayer", "ecr:BatchGetImage",
                                                                  "logs:CreateLogStream", "logs:PutLogEvents"]))

        task_definition = ecs.FargateTaskDefinition(self, "tsv_task_definition_petclinic", cpu=512, memory_limit_mib=2048,
                                                    execution_role=execution_role, family="tsv_task_definition_petclinic")

        image = ecs.ContainerImage.from_registry("docker push 355731635752.dkr.ecr.eu-central-1.amazonaws.com/petclinic:latest")
        container = task_definition.add_container("petclinic", image=image, secrets={
            "POSTGRES_PASSWORD": ecs.Secret.from_secrets_manager(db_secret, 'host'),
            "POSTGRES_USER": ecs.Secret.from_secrets_manager(db_secret, 'username'),
            "DB_PASS": ecs.Secret.from_secrets_manager(db_secret, 'password'),
        }, environment={"POSTGRES_DB": "postgres"},
                                                  logging=ecs.LogDriver.aws_logs(stream_prefix='stara'))
        container.add_port_mappings(ecs.PortMapping(container_port=8080))

        alb_fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(self, "venv-LB-petclinic",
                                                                                 cluster=cluster,
                                                                                 task_definition=task_definition,
                                                                                 desired_count=2,
                                                                                 cpu=512,
                                                                                 memory_limit_mib=2048,

                                                                                 public_load_balancer=True)
        self.service = alb_fargate_service.service
