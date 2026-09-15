import subprocess

terraform_dir = "/home/ubuntu/terraform-project"

try:
    # Step 1: Terraform Init
    subprocess.run(
        ["terraform", "init"],
        cwd=terraform_dir,
        check=True
    )

    print("Terraform init successful")

    # Step 2: Terraform Plan
    subprocess.run(
        ["terraform", "plan"],
        cwd=terraform_dir,
        check=True
    )

    print("Terraform plan successful")

    # Step 3: Terraform Apply
    subprocess.run(
        ["terraform", "apply", "-auto-approve"],
        cwd=terraform_dir,
        check=True
    )

    print("Terraform apply successful")

except subprocess.CalledProcessError as e:
    print(f"Terraform command failed: {e}")