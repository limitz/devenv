alias ls='ls -lFh --color=auto'
alias ll='ls -CF --color=auto'
alias la='ls -lFHa --color=auto'
alias search='apt-cache search'
alias install='sudo apt install -y --no-install-recommends'
alias make='make -j12'
alias find='~/.find.sh'
alias ecap='sudo /opt/EVT/eCapture/eCapture'
alias vimba='/usr/local/vimba/bin/VimbaViewer'
alias aliases='vi ~/.bash_aliases && source ~/.bash_aliases'
alias ssh-keygen='ssh-keygen -t ecdsa -b 512'

export CUDA_HOME=/usr/local/cuda
export TRT_HOME=/usr/src/tensorrt
export PATH=${CUDA_HOME}/bin:${TRT_HOME}/bin:${PATH}
export CPATH=${CUDA_HOME}/include:${CPATH}
export LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${CUDA_HOME}/bin:${LD_LIBRARY_PATH}
export LIBRARY_PATH=${CUDA_HOME}/lib64:${CUDA_HOME}/bin:${LIBRARY_PATH}
export TRT_DATADIR=${TRT_HOME}/data
