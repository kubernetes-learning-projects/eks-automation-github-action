import boto3
import json

def get_oidc_id(cluster_name, region):
    client = boto3.client('eks', region_name=region)
    response = client.describe_cluster(name=cluster_name)
    return response['cluster']['identity']['oidc']['issuer']

def update_trust_policy(role_name, trust_policy):
    iam_client = boto3.client('iam')
    iam_client.update_assume_role_policy(
        RoleName=role_name,
        PolicyDocument=json.dumps(trust_policy)
    )
    print("Trust policy updated successfully.")

def main():
    cluster_name = 'test-cluster'
    region = 'us-west-2'
    role_name = 'AmazonEKS_EBS_CSI_DriverRole'

    oidc_issuer = get_oidc_id(cluster_name, region)

    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Federated": f"arn:aws:iam::814200988517:oidc-provider/{oidc_issuer}"
                },
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringEquals": {
                        f"{oidc_issuer}:sub": "system:serviceaccount:kube-system:ebs-csi-controller-sa",
                        f"{oidc_issuer}:aud": "sts.amazonaws.com"
                    }
                }
            }
        ]
    }

    update_trust_policy(role_name, trust_policy)

if __name__ == "__main__":
    main()
