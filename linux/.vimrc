if &term == "screen"
	set t_Co=256
endif

filetype indent on
set mouse-=a
set ai
set incsearch
set number
set ignorecase
set smartcase
set wildmenu
set wildmode=list:longest,full
nnoremap <F2> :set invpaste paste?<CR>
set pastetoggle=<F2>
set showmode
colorscheme delek
syntax on

set tabstop=8 softtabstop=0 expandtab shiftwidth=4 smarttab
