#!/bin/bash
# Script to configure the EC2 instance for Django with Nginx and Gunicorn
# Adjust PROJECT_DIR and VENV_DIR if you upload it to a different path on EC2

PROJECT_DIR="/home/ubuntu/Face-Mask-Detection/backend"
VENV_DIR="/home/ubuntu/Face-Mask-Detection/venv"

echo "Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

echo "Installing Nginx, Python3-pip, Python3-venv..."
sudo apt-get install -y nginx python3-pip python3-venv

echo "Creating python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
fi

echo "Installing python dependencies..."
source $VENV_DIR/bin/activate
pip install -r $PROJECT_DIR/requirements.txt

# Run migrations and collect static
echo "Applying migrations..."
python $PROJECT_DIR/manage.py migrate
echo "Collecting static files..."
python $PROJECT_DIR/manage.py collectstatic --noinput

echo "Setting up Gunicorn systemd socket and service..."
sudo cp $PROJECT_DIR/deployment/gunicorn.socket /etc/systemd/system/
sudo cp $PROJECT_DIR/deployment/gunicorn.service /etc/systemd/system/

echo "Starting and enabling Gunicorn..."
sudo systemctl daemon-reload
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

echo "Setting up Nginx configuration..."
sudo cp $PROJECT_DIR/deployment/nginx.conf /etc/nginx/sites-available/face-mask-detection
sudo ln -sf /etc/nginx/sites-available/face-mask-detection /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

echo "Testing Nginx configuration..."
sudo nginx -t

echo "Restarting Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

echo "Allowing HTTP and OpenSSH through UFW firewall..."
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw --force enable

echo "Setup Complete!"
