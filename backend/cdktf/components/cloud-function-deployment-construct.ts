import { Construct } from "constructs";

import { ArchiveProvider } from "../.gen/providers/archive/provider";
import { GoogleAppEngineApplication } from "../.gen/providers/google-beta/google-app-engine-application";
import { GoogleStorageBucket } from "../.gen/providers/google-beta/google-storage-bucket";
import { RandomProvider } from "../.gen/providers/random/provider";
import { StringResource } from "../.gen/providers/random/string-resource";


export interface CloudFunctionDeploymentConstructProps {
    readonly project: string;
    readonly region: string;
    readonly randomProvider: RandomProvider;
    readonly archiveProvider: ArchiveProvider;
}

/**
 * Construct for Cloud Function deployment infrastructure.
 * Creates a storage bucket for function source code with automatic cleanup.
 * Note: Service enablement is handled separately in the main stack.
 */
export class CloudFunctionDeploymentConstruct extends Construct {
    public readonly sourceBucket: GoogleStorageBucket;
    public readonly project: string;
    public readonly region: string;

    constructor(scope: Construct, id: string, props: CloudFunctionDeploymentConstructProps) {
        super(scope, id);

        this.project = props.project;
        this.region = props.region;

        const bucketSuffix = new StringResource(this, "bucketPrefix", {
            length: 9,
            special: false,
            upper: false,
        })

        this.sourceBucket = new GoogleStorageBucket(this, "sourceBucket", {
            name: "source" + bucketSuffix.result,
            project: props.project,
            location: props.region,
            storageClass: "REGIONAL",
            forceDestroy: true,
            uniformBucketLevelAccess: true,
            lifecycleRule: [{
                action: {
                    type: "Delete"
                },
                condition: {
                    age: 1
                }
            }],
        });

        // Enable datastore API for the project (required for Cloud Functions)
        // https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/datastore_index
        new GoogleAppEngineApplication(this, "app-engine-application", {
            locationId: props.region,
            project: props.project,
            databaseType: "CLOUD_DATASTORE_COMPATIBILITY",
        });
    }
}