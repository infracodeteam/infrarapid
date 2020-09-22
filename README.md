# Templates generation for terraform

Infrarapid is a tool to generate terraform templates for your infrastructure

## Usage

- Clone the repo:

```bash
git clone https://github.com/infracodeteam/pytemplate.git
cd pytemplate
```

- Create a configuration file, you can find examples in
[`examples`](https://github.com/infracodeteam/pytemplate/tree/master/examples) folder
- Let's use [`aws-lite.yaml`](https://github.com/infracodeteam/pytemplate/blob/master/examples/aws-lite.yaml) file from examples:
- Run the script

```bash
python ./ic.py --config examples/aws-lite.yaml --templates-path results/
```

where `results` is path to folder to save Terraform templates into.

Then enter `results` directory and review your plan:

```bash
cd results/
terraform init
terraform plan
```

If everything is ok, run `terraform apply` to apply the configuration.

```bash
terraform appply
```
