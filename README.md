# AWS CloudFormation Template Collection

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![CI](https://github.com/jd-35656/aws-cft-collection/actions/workflows/deploy.yaml/badge.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
![Last Commit](https://img.shields.io/github/last-commit/jd-35656/aws-cft-collection)
![Issues](https://img.shields.io/github/issues/jd-35656/aws-cft-collection)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)

A curated and version-controlled collection of reusable **AWS CloudFormation
(CFT)** templates. This project is designed to streamline infrastructure
provisioning through modular, production-ready templates that follow AWS best
practices.

> ✅ Fully managed and maintained by
> [Jitesh Sahani (JD)](https://github.com/jd-35656)  
> ☁️ Templates are hosted publicly on S3 and can be integrated directly into
> CI/CD pipelines or IaC tools.

---

## Features

- 🧱 Modular and reusable CloudFormation templates
- ☁️ Public S3 hosting with versioned access
- ✅ AWS best-practice infrastructure patterns
- 🔁 Auto-updated README table with GitHub Actions
- 🚀 Ready to plug into any CI/CD or IaC workflow

---

## Usage

To deploy a CloudFormation template from this collection:

### Using AWS Console

1. Navigate to the
   [AWS CloudFormation Console](https://console.aws.amazon.com/cloudformation).
2. Choose **Create stack** → **With new resources (standard)**.
3. Under _Specify template_, select **Amazon S3 URL**.
4. Paste the desired template URL from the table below.
5. Follow the guided steps to configure stack parameters and deploy.

### Using AWS CLI

```bash
aws cloudformation create-stack \
  --stack-name STACK_NAME \
  --template-url TEMPLATE_S3_URL \
  --capabilities CAPABILITY_NAMED_IAM
```

> 💡 Replace the `--template-url` with the correct S3 link from the table below.

---

## Available Templates

This section provides a catalog of all available CloudFormation templates in
this repository, along with direct download links and S3 URLs for easy
integration.

<!-- markdownlint-disable MD013 -->
<!-- TEMPLATE TABLE START -->

| Name   | Description              | S3 URL                                                                                                                                 | Download Link                                                                                                                                    |
| ------ | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| sample | I am an example template | `https://jd-35656-public-collections.s3.ap-south-1.amazonaws.com/jd-35656/aws-cft-collection/main/cfts/templates/sample/template.yaml` | [download](https://jd-35656-public-collections.s3.ap-south-1.amazonaws.com/jd-35656/aws-cft-collection/main/cfts/templates/sample/template.yaml) |

<!-- TEMPLATE TABLE END -->
<!-- markdownlint-enable MD013 -->

---

## License

This project is licensed under the [MIT License](LICENSE).

---

Composed by [**_JD!_**](https://github.com/jd-35656)
