#!/bin/sh -

# Treat unset variables as an error.
set -o nounset

# Clone the botoform git repo.
git clone https://github.com/russellballestrini/botoform.git $HOME/botoform

# Change working directory to botoform source code root.
cd $HOME/botoform

echo "Assuming virtualenv is installed."

# Create a virtualenv named env. 
virtualenv env
source env/bin/activate

# Install dependencies into virtualenv.
python setup.py develop

echo "Verifying that the `bf` tool runs, running help to show usage."

# run help, should show usage.
bf --help

# Tell user the next step which is configuring the AWS Config file.
echo ""
echo "Botoform was installed successfully!"
echo ""

echo "Please configure your AWS Configuration file: `~/.aws/config`"
echo ""
echo "For help go to: "
echo "   https://botoform.readthedocs.io/en/latest/guides/quickstart.html#configuration"
