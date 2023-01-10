alias ls='ls -lFh --color=auto'
alias ll='ls -CF --color=auto'
alias la='ls -lFHa --color=auto'
alias search='apt-cache search'
alias install='sudo apt install -y --no-install-recommends'
alias make='make -j16'
alias aliases='vi ~/.bash_aliases && source ~/.bash_aliases'
alias sshconfig='vi ~/.ssh/config'

function findall(){
	sudo find / -iname *$1* 2>/dev/null
}

export CUDA_HOME=/usr/local/cuda
export TRT_HOME=/usr/src/tensorrt
export PATH=${CUDA_HOME}/bin:${TRT_HOME}/bin:${PATH}
export CPATH=${CUDA_HOME}/include:${CPATH}
export LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${CUDA_HOME}/bin:${LD_LIBRARY_PATH}
export LIBRARY_PATH=${CUDA_HOME}/lib64:${CUDA_HOME}/bin:${LIBRARY_PATH}
export TRT_DATADIR=${TRT_HOME}/data
