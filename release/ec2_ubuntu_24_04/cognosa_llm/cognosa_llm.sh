sudo apt update
sudo apt upgrade
sudo apt install -y linux-headers-$(uname -r) build-essential
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y nvidia-fabricmanager-580 cuda-toolkit-13-1 nvidia-open 
sudo apt install -y cuda-drivers
sudo apt install -y nvidia-gds

curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:70b-instruct-q4_0
ollama pull gemma3:27b

cp ollama.service /etc/systemd/system/ollama.service
sudo systemctl daemon-reload
sudo systemctl enable --now ollama
