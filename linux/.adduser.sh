sudo adduser $1 --disabled-password

sudo cp ~/.bashrc /home/$1
sudo cp ~/.bash_aliases /home/$1
sudo cp ~/.dircolors /home/$1
sudo cp ~/.tmux.conf /home/$1
sudo cp ~/.find.sh /home/$1

sudo mkdir -p /home/$1/.ssh

sudo ssh-keygen -t ecdsa -b 521 -f /home/$1/.ssh/id_$1 -q
sudo sh -c "cat /home/${1}/.ssh/id_${1}.pub >> /home/${1}/.ssh/authorized_keys"
sudo cat /home/$1/.ssh/id_$1
sudo cp /home/$1/.ssh/id_$1 ~/.ssh/
sudo chown -R $1:$1 /home/$1
sudo usermod -aG sudo $1
