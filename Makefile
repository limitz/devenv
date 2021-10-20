INSTALL = apt install -y --no-install-recommends


all: programs
	@echo "Installation complete"

programs:
	$(INSTALL) apt-utils tmux git-lfs git-flow 
	

