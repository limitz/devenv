# target name
TARGET = program

# Compiler and linker settings
CC 		:= gcc
LINKER		:= gcc

WFLAGS		:= -Wall -Wextra -Werror=float-equal -Wuninitialized -Wunused-variable -Wdouble-promotion
CFLAGS		:= -g -c -Wall -Iinclude
LDFLAGS		:= -pthread -lm

# Eye candy
TXT_MKDIR	:= MKDIR:  
TXT_COMPILE	:= COMPILE:
TXT_LINK	:= LINKED: 
TXT_DONE	:= All done!
TXT_CLEAN	:= All clean!

COLOR_TXT	:= \033[00;38;5;242m
COLOR_DIR	:= \033[00;38;5;248m
COLOR_OBJ	:= \033[01;38;5;248m
COLOR_EXE	:= \033[01;38;5;87m
COLOR_OK	:= \033[00;38;5;118m
EOL		:= \033[0m\n

# Directory and file settings
SRCDIR		:= src
INCDIR		:= include
OBJDIR		:= obj
OUTDIR		:= bin

SOURCES		:= $(wildcard $(SRCDIR)/*.c)
INCLUDES	:= $(wildcard $(INCDIR)/*.h)
OBJECTS		:= $(SOURCES:$(SRCDIR)/%.c=$(OBJDIR)/%.o)

# Installation settings
prefix		:= /usr/local
RM		:= rm -f
RMDIR		:= rm -rf
INSTALL		:= install -m 4755
INSTALLDIR	:= install -d -m 755

# Linking executable
$(OUTDIR)/$(TARGET): $(OBJECTS)
	@if [ ! -d "$(OUTDIR)" ]; then \
		mkdir $(OUTDIR); \
		printf "$(COLOR_TXT)$(TXT_MKDIR) $(COLOR_DIR)$(OUTDIR)/$(EOL)"; \
	fi
	@printf "$(COLOR_TXT)$(TXT_LINK) $(COLOR_EXE)$@$(EOL)"
	@$(LINKER) -o $@ $(OBJECTS) $(LDFLAGS)
	@echo "$(COLOR_OK)$(TXT_DONE)$(EOL)"

# Compiling obj files
$(OBJECTS): $(OBJDIR)/%.o : $(SRCDIR)/%.c $(INCLUDES)
	@if [ ! -d "$(OBJDIR)" ]; then \
		mkdir $(OBJDIR); \
		printf "$(COLOR_TXT)$(TXT_MKDIR) $(COLOR_DIR)$(OBJDIR)/$(EOL)"; \
	fi
	
	@$(CC) $(CFLAGS) $(WFLAGS) $(DEBUGFLAGS) $< -o $@
	@printf "$(COLOR_TXT)$(TXT_COMPILE) $(COLOR_OBJ)$@$(EOL)"


# Same as default
all: $(OUTDIR)/$(TARGET)

install:
	$(MAKE) --no-print-directory
	@$(INSTALLDIR) $(DESTDIR)$(prefix)/bin
	@$(INSTALL) $(OUTDIR)/$(TARGET) $(DESTDIR)$(prefix)/bin
	@echo "$(TARGET) installed"

clean:
	@$(RMDIR) $(OBJDIR)
	@$(RMDIR) $(OUTDIR)
	@echo "$(COLOR_OK)$(TXT_CLEAN)$(EOL)"

uninstall:
	@$(RM) $(DESTDIR)$(prefix)/bin/$(TARGET)
	@echo "$(TARGET) uninstalled"

