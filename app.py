#!/usr/bin/env python3

import aws_cdk as cdk

from infra.lib.CdkPipeline import CdkPipeline
#from infra.lib.push_image import push_image

app = cdk.App()
cdk_pipeline = CdkPipeline(app, "CdkPipelinePetclinic")
#push_image = push_image(app, "PushImage")


app.synth()
