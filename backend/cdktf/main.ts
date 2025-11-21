import { Construct } from "constructs";
import { App, TerraformOutput, TerraformStack } from "cdktf";
import { ArchiveProvider } from "./.gen/providers/archive/provider";
import { RandomProvider } from "./.gen/providers/random/provider";
import { StringResource } from "./.gen/providers/random/string-resource";
import { DataGoogleBillingAccount } from "./.gen/providers/google-beta/data-google-billing-account";
import { GoogleBetaProvider } from "./.gen/providers/google-beta/provider/index";
import { GoogleProject } from "./.gen/providers/google-beta/google-project";
import { CloudFunctionDeploymentConstruct } from "./components/cloud-function-deployment-construct";
import { CloudFunctionConstruct } from "./components/cloud-function-construct";
import { ApigatewayConstruct } from "./components/api-gateway-construct";
import { GoogleProjectIamMember } from "./.gen/providers/google-beta/google-project-iam-member";
import { GoogleStorageBucketIamMember } from "./.gen/providers/google-beta/google-storage-bucket-iam-member";
import * as dotenv from 'dotenv';
import { FirestoreConstruct } from "./components/firestore-construct";
import { GoogleStorageBucket } from "./.gen/providers/google-beta/google-storage-bucket";

dotenv.config();

class XiaoiceApiStack extends TerraformStack {
  constructor(scope: Construct, id: string) {
    super(scope, id);
  }

  async buildXiaoiceApiStack() {
    const projectId = process.env.PROJECTID!;

    const googleBetaProvider = new GoogleBetaProvider(this, "google", {
      region: process.env.REGION!,
    });
    const archiveProvider = new ArchiveProvider(this, "archive", {});
    const randomProvider = new RandomProvider(this, "random", {});

    const billingAccount = new DataGoogleBillingAccount(this, "billing-account", {
      billingAccount: process.env.BILLING_ACCOUNT!,
    });

    const project = new GoogleProject(this, "project", {
      projectId: projectId,
      name: projectId,
      billingAccount: billingAccount.id,
      deletionPolicy: "DELETE",
    });



    const cloudFunctionDeploymentConstruct = new CloudFunctionDeploymentConstruct(this, "cloud-function-deployment", {
      project: project.projectId,
      randomProvider: randomProvider,
      archiveProvider: archiveProvider,
      region: process.env.REGION!,
    });

    const speechBucketSuffix = new StringResource(this, "speechFileBucketSuffix", {
      length: 9,
      special: false,
      upper: false,
    });

    const speechFileBucket =new GoogleStorageBucket(this, "speechFileBucket", {
          // Grant storage.objectAdmin to speech function service account for bucket access
      name: "speechfile" + speechBucketSuffix.result,
      project: project.projectId,
      location: process.env.REGION!,
      storageClass: "REGIONAL",
      forceDestroy: true,
      uniformBucketLevelAccess: true,
      lifecycleRule: [{
        action: {
          type: "Delete",
        },
        condition: {
          age: 1,
        },
      }],
      dependsOn: cloudFunctionDeploymentConstruct.services,
    });

    const artifactRegistryIamMember = new GoogleProjectIamMember(this, "cloud-functions-artifact-registry-reader", {
      project: projectId,
      role: "roles/artifactregistry.reader",
      member: `serviceAccount:service-${project.number}@gcf-admin-robot.iam.gserviceaccount.com`,
      dependsOn: cloudFunctionDeploymentConstruct.services,
    });

    const talkStreamFunction = await CloudFunctionConstruct.create(this, "talkStreamFunction", {
      functionName: "talk-stream",
      runtime: "python311",
      entryPoint: "talk_stream",
      timeout: 1200,
      availableCpu: "2",
      availableMemory: "2048Mi",
      makePublic: false,
      cloudFunctionDeploymentConstruct: cloudFunctionDeploymentConstruct,
      environmentVariables: {
        "XIAOICE_CHAT_SECRET_KEY": process.env.XIAOICE_CHAT_SECRET_KEY || "default_secret_key",
        "XIAOICE_CHAT_ACCESS_KEY": process.env.XIAOICE_CHAT_ACCESS_KEY || "default_access_key",
        "GOOGLE_CLOUD_PROJECT": projectId,
        "GOOGLE_CLOUD_LOCATION": "global",
        "GOOGLE_GENAI_USE_VERTEXAI": "True"
      },
      additionalDependencies: [artifactRegistryIamMember],
    });

    // Grant AI Platform (Vertex AI) user role to the service account for Gemini API access
    // (declaration moved below after all CloudFunctionConstruct.create calls)
    const aiPlatformIamMember = new GoogleProjectIamMember(this, "ai-platform-user", {
      project: projectId,
      role: "roles/aiplatform.user",
      member: `serviceAccount:${talkStreamFunction.serviceAccount.email}`,
      dependsOn: cloudFunctionDeploymentConstruct.services,
    });

    // Allow writing to the client's Firestore project (xiaoice-class-assistant)
    // This is required because of the project ID mismatch (backend=xiaice... vs client=xiaoice...)
    new GoogleProjectIamMember(this, "cross-project-firestore-writer", {
      project: "xiaoice-class-assistant",
      role: "roles/datastore.user",
      member: `serviceAccount:${talkStreamFunction.serviceAccount.email}`,
    });

    const welcomeFunction = await CloudFunctionConstruct.create(this, "welcomeFunction", {
      functionName: "welcome",
      runtime: "python311",
      entryPoint: "welcome",
      timeout: 60,
      availableMemory: "256Mi",
      makePublic: false,
      cloudFunctionDeploymentConstruct: cloudFunctionDeploymentConstruct,
      serviceAccount: talkStreamFunction.serviceAccount,
      environmentVariables: {
        "XIAOICE_CHAT_SECRET_KEY": process.env.XIAOICE_CHAT_SECRET_KEY || "default_secret_key",
        "XIAOICE_CHAT_ACCESS_KEY": process.env.XIAOICE_CHAT_ACCESS_KEY || "default_access_key",
      },
      additionalDependencies: [artifactRegistryIamMember, aiPlatformIamMember],
    });
    const speechFunction = await CloudFunctionConstruct.create(this, "speechFunction", {
      functionName: "speech",
      runtime: "python311",
      entryPoint: "speech",
      timeout: 60,
      availableMemory: "256Mi",
      makePublic: false,
      cloudFunctionDeploymentConstruct: cloudFunctionDeploymentConstruct,
      serviceAccount: talkStreamFunction.serviceAccount,
      environmentVariables: {
        "XIAOICE_CHAT_SECRET_KEY": process.env.XIAOICE_CHAT_SECRET_KEY || "default_secret_key",
        "XIAOICE_CHAT_ACCESS_KEY": process.env.XIAOICE_CHAT_ACCESS_KEY || "default_access_key",
        "SPEECH_FILE_BUCKET": speechFileBucket.name,
      },
      additionalDependencies: [artifactRegistryIamMember, aiPlatformIamMember],
    });
    // Grant storage.objectAdmin to speech function service account for bucket access and signed URL generation
    new GoogleProjectIamMember(this, "speech-bucket-object-admin", {
      project: projectId,
      role: "roles/storage.objectAdmin",
      member: `serviceAccount:${talkStreamFunction.serviceAccount.email}`,
      dependsOn: cloudFunctionDeploymentConstruct.services,
    });
    // Grant Service Account Token Creator role to allow the service account to sign on behalf of itself
    // Public read access for speech bucket (serving MP3 directly)
    new GoogleStorageBucketIamMember(this, "speech-bucket-public-read", {
      bucket: speechFileBucket.name,
      role: "roles/storage.objectViewer",
      member: "allUsers",
      dependsOn: [speechFileBucket],
    });
    const goodbyeFunction = await CloudFunctionConstruct.create(this, "goodbyeFunction", {
      functionName: "goodbye",
      runtime: "python311",
      entryPoint: "goodbye",
      timeout: 60,
      availableMemory: "256Mi",
      makePublic: false,
      cloudFunctionDeploymentConstruct: cloudFunctionDeploymentConstruct,
      serviceAccount: talkStreamFunction.serviceAccount,
      environmentVariables: {
        "XIAOICE_CHAT_SECRET_KEY": process.env.XIAOICE_CHAT_SECRET_KEY || "default_secret_key",
        "XIAOICE_CHAT_ACCESS_KEY": process.env.XIAOICE_CHAT_ACCESS_KEY || "default_access_key",
      },
      additionalDependencies: [artifactRegistryIamMember, aiPlatformIamMember],
    });
    const recquestionsFunction = await CloudFunctionConstruct.create(this, "recquestionsFunction", {
      functionName: "recquestions",
      runtime: "python311",
      entryPoint: "recquestions",
      timeout: 60,
      availableMemory: "256Mi",
      makePublic: false,
      cloudFunctionDeploymentConstruct: cloudFunctionDeploymentConstruct,
      serviceAccount: talkStreamFunction.serviceAccount,
      environmentVariables: {
        "XIAOICE_CHAT_SECRET_KEY": process.env.XIAOICE_CHAT_SECRET_KEY || "default_secret_key",
        "XIAOICE_CHAT_ACCESS_KEY": process.env.XIAOICE_CHAT_ACCESS_KEY || "default_access_key",
      },
      additionalDependencies: [artifactRegistryIamMember, aiPlatformIamMember],
    });

    const configFunction = await CloudFunctionConstruct.create(this, "configFunction", {
      functionName: "config",
      runtime: "python311",
      entryPoint: "config",
      timeout: 1200,
      availableCpu: "2",
      availableMemory: "2048Mi",
      makePublic: false,
      cloudFunctionDeploymentConstruct: cloudFunctionDeploymentConstruct,
      serviceAccount: talkStreamFunction.serviceAccount,
      environmentVariables: {
        "GOOGLE_CLOUD_PROJECT": projectId,
        "GOOGLE_CLOUD_LOCATION": "global",
        "GOOGLE_GENAI_USE_VERTEXAI": "True",
        "SPEECH_FILE_BUCKET": speechFileBucket.name,
      },
      additionalDependencies: [artifactRegistryIamMember, aiPlatformIamMember],
    });

    const apigatewayConstruct = await ApigatewayConstruct.create(this, "api-gateway", {
      api: "xiaoiceapi",
      project: project.projectId,
      provider: googleBetaProvider,
      replaces: {
        "TALK_STREAM": talkStreamFunction.cloudFunction.url,
        "WELCOME": welcomeFunction.cloudFunction.url,
        "SPEECH": speechFunction.cloudFunction.url,
        "GOODBYE": goodbyeFunction.cloudFunction.url,
        "RECQUESTIONS": recquestionsFunction.cloudFunction.url,
        "CONFIG": configFunction.cloudFunction.url
      },
      servicesAccount: talkStreamFunction.serviceAccount,
    });

    FirestoreConstruct.create(this, "firestore", {
      project: project.projectId,
      servicesAccount: talkStreamFunction.serviceAccount
    });

    new TerraformOutput(this, "project-id", {
      value: project.projectId,
    });

    new TerraformOutput(this, "api-url", {
      value: apigatewayConstruct.gateway.defaultHostname,
    });

    new TerraformOutput(this, "api-service-name", {
      value: apigatewayConstruct.apiGatewayApi.managedService,
    });
    new TerraformOutput(this, "speech-file-bucket", {
      value: speechFileBucket.name,
    });
  }
}

async function buildStack(scope: Construct, id: string) {
  const stack = new XiaoiceApiStack(scope, id);
  await stack.buildXiaoiceApiStack();
}

async function createApp(): Promise<App> {
  const app = new App();
  await buildStack(app, "cdktf");
  return app;
}

createApp().then((app) => app.synth());
